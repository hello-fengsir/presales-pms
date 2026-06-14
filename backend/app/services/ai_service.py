"""AI-powered services — modular provider support via saved API keys."""
import json
import os
import httpx
import logging
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Legacy fallback (from docker env)
LEGACY_DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE = "https://api.deepseek.com"

PARSE_NOTES_PROMPT = """你是一位售前工程师助手。请从以下会议纪要中提取关键信息，输出严格的 JSON 格式（不要 Markdown 包裹）。

如果某个字段无法从会议纪要中推断，用空字符串 "" 或 null。

JSON 格式：
{
  "project_name": "项目名称（简短概括，15字以内）",
  "customer_name": "客户公司名称",
  "amount": 预估金额（数字，万元单位，无则 null）,
  "stage": "线索/需求确认/方案报价/商务谈判（根据内容判断）",
  "sales_mode": "直客/渠道",
  "customer_background": "客户背景（从纪要中提取）",
  "customer_requirement": "客户需求（分点列出，每点用数字1. 2.开头）",
  "solution_description": "方案描述（如果有提到技术方案的话）",
  "competitor_info": "竞品信息（如果提到竞争对手的话）",
  "key_contacts": "关键联系人及角色",
  "next_steps": "下一步计划",
  "risk_points": "风险点"
}

会议纪要内容：
{notes}
"""

# ── Customer Enrichment Prompt ──
ENRICH_CUSTOMER_PROMPT = """你是一位企业信息分析师。请根据给定的公司名称，输出该公司的关键企业信息，严格 JSON 格式（不要 Markdown 包裹）。

如果你不了解这家公司，请根据公司名称合理推断最可能的行业和规模，标注 confidence 为 "low"。
如果你确定了解这家公司，标注 confidence 为 "high"。

JSON 格式（单家公司）：
{
  "industry": "所属行业（如：金融、互联网、电商、制造、教育、医疗、物流、能源等，简短明确，8字以内）",
  "scale": "公司规模（如：100-500人、1000人以上、上市公司、初创公司等）",
  "region": "总部所在城市（如：北京、上海、深圳、杭州等，4字以内）",
  "notes": "公司简介（一句话概括主营业务，50字以内）",
  "confidence": "high 或 low"
}

公司名称：
{company_name}

请只输出以上 JSON，不要添加任何其他文字。"""


def _get_active_key(db_session, provider: str, model: str = None) -> dict | None:
    """Look up the active API key from the database for the given provider."""
    from ..modules.presales.models import ApiKey
    q = select(ApiKey).where(ApiKey.provider == provider, ApiKey.is_active == True)
    if model:
        q = q.where(ApiKey.model == model)
    q = q.order_by(ApiKey.updated_at.desc()).limit(1)
    row = db_session.scalars(q).first()
    if row:
        return {"api_key": row.api_key, "base_url": row.base_url, "model": row.model, "provider": row.provider}
    return None


async def _call_llm(api_key: str, base_url: str, model: str, prompt: str, system: str = "") -> str:
    """Generic LLM call via OpenAI-compatible API."""
    url = base_url.rstrip("/")
    if "/chat/completions" not in url:
        if "/v1" in url:
            url += "/chat/completions"
        else:
            url += "/v1/chat/completions"

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system or "你是一个专业的数据提取助手，严格输出 JSON，不要添加任何解释。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 2000,
            },
        )
        data = resp.json()
    return data["choices"][0]["message"]["content"]


def _extract_json(content: str) -> dict:
    """Extract and parse JSON from LLM response."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        content = content[start:end+1]
    return json.loads(content)


async def enrich_customer_info(company_name: str, db_session=None, provider: str = None, model: str = None) -> dict:
    """Enrich a single customer's company info using AI.

    Returns dict with: industry, scale, region, notes, confidence
    """
    # Get API key (same logic as parse_meeting_notes)
    api_key = None
    base_url = None
    llm_model = None

    if db_session is not None:
        key_info = None
        if provider:
            key_info = _get_active_key(db_session, provider, model)
        else:
            for p in ["deepseek", "qwen", "zhipu", "moonshot", "doubao"]:
                key_info = _get_active_key(db_session, p)
                if key_info:
                    break

        if key_info:
            api_key = key_info["api_key"]
            base_url = key_info["base_url"]
            llm_model = key_info["model"]

    if not api_key and LEGACY_DEEPSEEK_KEY:
        api_key = LEGACY_DEEPSEEK_KEY
        base_url = DEEPSEEK_BASE
        llm_model = model or "deepseek-chat"

    if not api_key:
        raise ValueError("AI 引擎未配置。请在左下角「API配置」中添加至少一个 API Key。")

    prompt = ENRICH_CUSTOMER_PROMPT.replace("{company_name}", company_name)
    system = "你是一个企业信息分析师。根据你的训练数据知识，输出中国公司的基本信息。只返回JSON。"
    content = await _call_llm(api_key, base_url, llm_model, prompt, system)
    return _extract_json(content)


async def enrich_customers_batch(company_names: list[str], db_session=None) -> list[dict]:
    """Enrich multiple customers — process sequentially to avoid rate limits.

    Returns list of {company_name, industry, scale, region, notes, confidence, error}
    """
    results = []
    for name in company_names:
        try:
            info = await enrich_customer_info(name, db_session=db_session)
            info["company_name"] = name
            info["error"] = None
            results.append(info)
        except Exception as e:
            logger.warning(f"Failed to enrich {name}: {e}")
            results.append({
                "company_name": name,
                "industry": "",
                "scale": "",
                "region": "",
                "notes": "",
                "confidence": "low",
                "error": str(e),
            })
    return results


async def parse_meeting_notes(notes: str, db_session=None, provider: str = None, model: str = None) -> dict:
    """Parse meeting notes into structured project data.

    Priority:
    1. User-specified provider/model -> look up saved key from DB
    2. If not specified, try first active key from DB
    3. Fall back to legacy DEEPSEEK_API_KEY env var
    """
    api_key = None
    base_url = None
    llm_model = None

    # Try DB lookup first
    if db_session is not None:
        key_info = None
        if provider:
            key_info = _get_active_key(db_session, provider, model)
        else:
            # Try each provider in order of preference
            for p in ["deepseek", "qwen", "zhipu", "moonshot", "doubao"]:
                key_info = _get_active_key(db_session, p)
                if key_info:
                    break

        if key_info:
            api_key = key_info["api_key"]
            base_url = key_info["base_url"]
            llm_model = key_info["model"]
            logger.info(f"Using saved API key: {key_info.get('provider', '')}/{llm_model}")

    # Fallback to legacy env var
    if not api_key and LEGACY_DEEPSEEK_KEY:
        api_key = LEGACY_DEEPSEEK_KEY
        base_url = DEEPSEEK_BASE
        llm_model = model or "deepseek-chat"
        logger.info("Using legacy DeepSeek key (env var)")

    if not api_key:
        logger.error("No API key configured")
        raise ValueError("AI 引擎未配置。请在左下角「API配置」中添加至少一个 API Key。")

    prompt = PARSE_NOTES_PROMPT.replace("{notes}", notes[:3000])
    content = await _call_llm(api_key, base_url, llm_model, prompt)
    return _extract_json(content)

EXTRACT_CUSTOMER_PROMPT = """你是一个企业信息提取助手。根据用户提供的文本，提取该公司的结构化信息。

规则：
1. 只返回JSON，不要解释
2. 如果文本中没有某字段信息，用空字符串
3. 字段含义：industry=行业, scale=规模(如"100-500人"或"上市公司"), region=所在城市/区域, notes=公司简介/业务描述(50字以内)

用户提供的文本：
{raw_text}

请返回JSON：
{"industry": "", "scale": "", "region": "", "notes": "", "confidence": "high|medium|low"}
"""

async def extract_customer_from_text(raw_text: str, company_name: str = "", db_session=None) -> dict:
    """Extract structured customer info from raw text using AI."""
    api_key = None
    base_url = None
    llm_model = None
    
    if db_session is not None:
        for p in ["deepseek", "qwen", "zhipu", "moonshot", "doubao"]:
            key_info = _get_active_key(db_session, p)
            if key_info:
                api_key = key_info["api_key"]
                base_url = key_info["base_url"]
                llm_model = key_info["model"]
                break
    
    if not api_key and LEGACY_DEEPSEEK_KEY:
        api_key = LEGACY_DEEPSEEK_KEY
        base_url = DEEPSEEK_BASE
        llm_model = "deepseek-chat"
    
    if not api_key:
        raise ValueError("AI 引擎未配置。请在左下角「API配置」中添加至少一个 API Key。")
    
    prompt = EXTRACT_CUSTOMER_PROMPT.replace("{raw_text}", raw_text)
    if company_name:
        prompt = prompt.replace("{company_name}", company_name)
    system = "你是一个企业信息提取助手。只返回JSON。"
    content = await _call_llm(api_key, base_url, llm_model, prompt, system)
    return _extract_json(content)
