// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface User {
  username: string
  role: string
  is_active: boolean
}

export interface AuthState {
  token: string | null
  user: User | null
  setAuth: (token: string, user: User) => void
  logout: () => void
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export interface ChatResponse {
  answer: string
  sources: string[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
}

// ─── Ingest ───────────────────────────────────────────────────────────────────

export interface IngestResponse {
  message: string
  chunks_added: number
}

export interface IngestUrlsRequest {
  urls: string[]
}

// ─── Collections ──────────────────────────────────────────────────────────────

export interface Collection {
  name: string
  vectors: number
}

export interface CollectionsResponse {
  total_collections: number
  total_vectors: number
  collections: Collection[]
}

// ─── API Error ────────────────────────────────────────────────────────────────

export interface ApiErrorDetail {
  detail: string
}
