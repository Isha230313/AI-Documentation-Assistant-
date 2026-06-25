import { apiClient } from './client'

export const getSources = (): Promise<string[]> =>
  apiClient.get('/sources').then((r) => r.data)

export const deleteSource = (source: string): Promise<{ message: string }> =>
  apiClient.delete('/sources', { data: { source } }).then((r) => r.data)
