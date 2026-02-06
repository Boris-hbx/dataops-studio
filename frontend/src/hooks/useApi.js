import { useState, useEffect, useCallback } from 'react'

/**
 * 通用 API 请求 Hook — 封装 fetch → json → setState + loading/error/refetch
 * @param {string} url - API 地址
 * @param {object} [options] - { defaultValue, immediate }
 * @returns {{ data, loading, error, refetch }}
 */
export default function useApi(url, options = {}) {
  const { defaultValue = null, immediate = true } = options
  const [data, setData] = useState(defaultValue)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)

  const refetch = useCallback(() => {
    setLoading(true)
    setError(null)
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [url])

  useEffect(() => {
    if (immediate) refetch()
  }, [immediate, refetch])

  return { data, loading, error, refetch }
}
