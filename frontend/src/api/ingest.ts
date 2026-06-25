import { apiClient } from './client'
import type { IngestResponse, IngestUrlsRequest } from '../types'

export async function ingestFiles(
  files: File[],
  onUploadProgress?: (percent: number) => void
): Promise<IngestResponse> {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))

  const response = await apiClient.post<IngestResponse>('/ingest/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onUploadProgress && event.total) {
        onUploadProgress(Math.round((event.loaded * 100) / event.total))
      }
    },
  })
  return response.data
}

export async function ingestUrls(request: IngestUrlsRequest): Promise<IngestResponse> {
  const response = await apiClient.post<IngestResponse>('/ingest/urls', request)
  return response.data
}
