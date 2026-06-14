"""国内主流大模型服务商配置"""
PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek (深度求索)",
        "base_url": "https://api.deepseek.com",
        "models": [
            {"id": "deepseek-v4-pro", "name": "V4-Pro (2026.04)"},
            {"id": "deepseek-v4-flash", "name": "V4-Flash (2026.04)"},
            {"id": "deepseek-chat", "name": "DeepSeek-Chat"},
        ],
        "api_path": "/v1/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "qwen": {
        "name": "阿里云 (通义千问)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": [
            {"id": "qwen3.7-max", "name": "Qwen3.7-Max (2026.05)"},
            {"id": "qwen3.7-plus", "name": "Qwen3.7-Plus (2026.05)"},
            {"id": "qwen-plus", "name": "Qwen-Plus"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "zhipu": {
        "name": "智谱AI (GLM)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": [
            {"id": "glm-5.1", "name": "GLM-5.1 高速版 (2026.05)"},
            {"id": "glm-4.7-flash", "name": "GLM-4.7-Flash (2026.01)"},
            {"id": "glm-4-plus", "name": "GLM-4-Plus"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "moonshot": {
        "name": "月之暗面 (Kimi)",
        "base_url": "https://api.moonshot.cn/v1",
        "models": [
            {"id": "kimi-k2.5", "name": "Kimi K2.5 (2026.01)"},
            {"id": "moonshot-v1-8k", "name": "Moonshot v1-8K"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "doubao": {
        "name": "字节跳动 (豆包)",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": [
            {"id": "doubao-pro-2.0", "name": "豆包 2.0 Pro (2026.02)"},
            {"id": "doubao-lite-2.0", "name": "豆包 2.0 Lite (2026.02)"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "minimax": {
        "name": "MiniMax",
        "base_url": "https://api.minimax.chat/v1",
        "models": [
            {"id": "minimax-m3", "name": "MiniMax M3 (2026.06)"},
        ],
        "api_path": "/text/chatcompletion_v2",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5,
        },
    },
    "baidu": {
        "name": "百度 (文心一言)",
        "base_url": "https://qianfan.baidubce.com/v2",
        "models": [
            {"id": "ernie-5.1", "name": "文心大模型 5.1 (2026.05)"},
            {"id": "ernie-4.0-turbo", "name": "ERNIE 4.0 Turbo"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "tencent": {
        "name": "腾讯 (混元)",
        "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
        "models": [
            {"id": "hunyuan-hy3-preview", "name": "混元 Hy3 Preview (2026.04)"},
            {"id": "hunyuan-turbo", "name": "混元 Turbo"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
    "sensetime": {
        "name": "商汤科技 (日日新 SenseNova)",
        "base_url": "https://api.sensenova.cn/v1",
        "models": [
            {"id": "sensenova-6.7-flash-lite", "name": "6.7 Flash-Lite (2026.05)"},
        ],
        "api_path": "/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "test_body": lambda model: {
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5
        },
    },
}
