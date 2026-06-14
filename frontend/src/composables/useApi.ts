import { ref, type Ref } from 'vue'
import type { AxiosResponse } from 'axios'

interface UseApiReturn<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  refresh: () => Promise<void>
}

export function useApi<T>(
  fetcher: () => Promise<AxiosResponse<any>>
): UseApiReturn<T> {
  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function refresh() {
    loading.value = true
    error.value = null
    try {
      const res = await fetcher()
      data.value = (res.data?.data ?? res.data) as T
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? e?.message ?? '请求失败'
      error.value = msg
    } finally {
      loading.value = false
    }
  }

  refresh()
  return { data, loading, error, refresh }
}
