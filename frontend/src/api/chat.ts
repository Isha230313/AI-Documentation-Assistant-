import { apiClient } from './client'
import type { ChatResponse } from '../types'

export async function sendMessage(request: { question: string }): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat', request)
  return response.data
}
