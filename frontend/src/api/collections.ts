import { apiClient } from './client'
import type { CollectionsResponse } from '../types'

/**
 * Fetch vector store collection statistics.
 */
export async function getCollections(): Promise<CollectionsResponse> {
  const response = await apiClient.get<CollectionsResponse>('/collections')
  return response.data
}
