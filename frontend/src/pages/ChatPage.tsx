import { useState, useRef, useEffect, type FormEvent, type KeyboardEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import ReactMarkdown from 'react-markdown'
import { sendMessage } from '../api/chat'
import Layout from '../components/Layout'
import Spinner from '../components/Spinner'
import { useThemeStore } from '../store/theme'
import type { ChatMessage } from '../types'

function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 animate-fade-in">
      <div className="w-8 h-8 shrink-0 rounded-full flex items-center justify-center text-xs font-bold text-white"
        style={{ background: 'linear-gradient(135deg, #3b82f6, #06b6d4)' }}>
        AI
      </div>
      <div className="glass-card px-4 py-3 max-w-xs">
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <span key={i} className="w-1.5 h-1.5 rounded-full bg-blue-400"
              style={{ animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }} />
          ))}
        </div>
      </div>
    </div>
  )
}

function Sources({ sources }: { sources: string[] }) {
  const [open, setOpen] = useState(false)
  if (sources.length === 0) return null

  return (
    <div className="mt-2.5">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-blue-500 hover:text-cyan-600 dark:text-blue-400/80 dark:hover:text-cyan-300 transition-colors"
      >
        <svg className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-90' : ''}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span>{sources.length} source{sources.length !== 1 ? 's' : ''}</span>
      </button>

      {open && (
        <ul className="mt-2 space-y-1 animate-fade-in">
          {sources.map((src, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-blue-400 text-xs mt-0.5 shrink-0">›</span>
              <span className="text-xs text-gray-500 dark:text-white/50 break-all leading-relaxed">{src}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === 'user') {
    return (
      <div className="flex items-end justify-end gap-3 animate-fade-in">
        <div className="flex flex-col items-end gap-1 max-w-[72%]">
          <div className="px-4 py-3 rounded-2xl rounded-br-md text-sm leading-relaxed text-white"
            style={{ background: 'linear-gradient(135deg, #3b82f6, #06b6d4)', boxShadow: '0 4px 20px rgba(59,130,246,0.25)' }}>
            {message.content}
          </div>
        </div>
        <div className="w-8 h-8 shrink-0 rounded-full flex items-center justify-center text-xs font-bold text-white"
          style={{ background: 'linear-gradient(135deg, #06b6d4, #38bdf8)' }}>
          U
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-end gap-3 animate-fade-in">
      <div className="w-8 h-8 shrink-0 rounded-full flex items-center justify-center text-xs font-bold text-white"
        style={{ background: 'linear-gradient(135deg, #3b82f6, #06b6d4)' }}>
        AI
      </div>
      <div className="flex flex-col gap-1 max-w-[72%]">
        <div className="glass-card px-4 py-3 text-sm leading-relaxed text-gray-800 dark:text-white/90 prose-ai">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="text-xl font-bold mt-4 mb-2 bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent border-b border-blue-400/30 pb-1">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-base font-bold mt-3 mb-1.5 text-blue-500 dark:text-cyan-300">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold mt-2.5 mb-1 text-blue-400 dark:text-cyan-400/80">
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="mb-2 ml-4 list-disc space-y-0.5">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="mb-2 ml-4 list-decimal space-y-0.5">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="leading-relaxed">{children}</li>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-gray-900 dark:text-white">{children}</strong>
              ),
              code: ({ children }) => (
                <code className="px-1 py-0.5 rounded text-xs font-mono bg-blue-50 dark:bg-white/10 text-blue-700 dark:text-cyan-300">
                  {children}
                </code>
              ),
              table: ({ children }) => (
                <div className="overflow-x-auto my-3">
                  <table className="w-full text-xs border-collapse">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-gradient-to-r from-blue-500/20 to-cyan-400/20">
                  {children}
                </thead>
              ),
              tbody: ({ children }) => (
                <tbody className="divide-y divide-blue-400/10">
                  {children}
                </tbody>
              ),
              tr: ({ children }) => (
                <tr className="hover:bg-blue-400/5 transition-colors">
                  {children}
                </tr>
              ),
              th: ({ children }) => (
                <th className="px-3 py-2 text-left font-semibold text-blue-500 dark:text-cyan-300 border border-blue-400/20">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-3 py-2 text-gray-700 dark:text-white/80 border border-blue-400/10">
                  {children}
                </td>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
          {message.sources && <Sources sources={message.sources} />}
        </div>
      </div>
    </div>
  )
}

const SUGGESTIONS = [
  'How do I get started?',
  'How does it work?',
  'What are the key features?',
  'Show me an example',
]

function EmptyState({ onSuggest }: { onSuggest: (q: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-6 py-16 animate-fade-in">
      <div className="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl mb-6"
        style={{ background: 'linear-gradient(135deg, rgba(59,130,246,0.1), rgba(6,182,212,0.1))', border: '1px solid rgba(59,130,246,0.2)' }}>
        💬
      </div>
      <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">Ask your docs anything</h2>
      <p className="text-sm mb-8 text-center max-w-sm text-gray-500 dark:text-white/40">
        I can answer questions about your documentation. Try one of these to get started:
      </p>
      <div className="flex flex-wrap gap-3 justify-center max-w-lg">
        {SUGGESTIONS.map((q) => (
          <button key={q} onClick={() => onSuggest(q)}
            className="px-4 py-2.5 rounded-xl text-sm font-medium text-blue-600 dark:text-cyan-300 hover:scale-105 transition-all duration-200"
            style={{ background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.3)' }}>
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const { isDark } = useThemeStore()
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try {
      const saved = localStorage.getItem('chat_history')
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })
  const [input, setInput] = useState('')
  const [apiError, setApiError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(messages))
  }, [messages])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [input])

  const sendMutation = useMutation({
    mutationFn: (question: string) => sendMessage({ question }),
    onSuccess: (data) => {
      setApiError(null)
      setMessages((prev) => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }])
    },
    onError: (error: unknown) => {
      setMessages((prev) => prev.slice(0, -1))
      if (error instanceof AxiosError) {
        setApiError(error.response?.data?.detail ?? 'Failed to get a response. Please try again.')
      } else {
        setApiError('An unexpected error occurred. Please try again.')
      }
    },
  })

  const handleSubmit = (question?: string) => {
    const text = (question ?? input).trim()
    if (!text || sendMutation.isPending) return
    setApiError(null)
    setInput('')
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content: text }])
    sendMutation.mutate(text)
  }

  const handleFormSubmit = (e: FormEvent) => { e.preventDefault(); handleSubmit() }
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit() }
  }
  const handleClear = () => { setMessages([]); setApiError(null); sendMutation.reset(); localStorage.removeItem('chat_history') }

  return (
    <Layout>
      <div className="flex flex-col h-full min-h-0" style={{ height: 'calc(100vh - 65px)' }}>
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {messages.length === 0 && !sendMutation.isPending ? (
            <EmptyState onSuggest={handleSubmit} />
          ) : (
            <div className="max-w-3xl mx-auto w-full px-4 py-6 space-y-6">
              {messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)}
              {sendMutation.isPending && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {apiError && (
          <div className="max-w-3xl mx-auto w-full px-4 pb-2 animate-fade-in">
            <div className="error-banner" role="alert">
              <span>{apiError}</span>
              <button onClick={() => setApiError(null)}
                className="ml-auto text-red-400 hover:text-red-600 text-lg leading-none" aria-label="Dismiss">
                ×
              </button>
            </div>
          </div>
        )}

        <div className="shrink-0 px-4 py-4" style={{ borderTop: isDark ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(0,0,0,0.06)' }}>
          <form onSubmit={handleFormSubmit} className="max-w-3xl mx-auto flex items-end gap-3">
            <div className="flex-1 flex items-end gap-2 rounded-2xl px-4 py-3"
              style={{
                background: isDark ? 'rgba(255,255,255,0.05)' : '#f3f4f6',
                border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
              }}>
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your documentation…"
                disabled={sendMutation.isPending}
                rows={1}
                className={`flex-1 bg-transparent text-sm resize-none outline-none leading-relaxed scrollbar-thin disabled:opacity-50
                  ${isDark ? 'text-white placeholder-white/30' : 'text-gray-900 placeholder-gray-400'}`}
                style={{ maxHeight: '160px', minHeight: '24px' }}
                aria-label="Chat input"
              />
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {messages.length > 0 && (
                <button type="button" onClick={handleClear} disabled={sendMutation.isPending}
                  className="ghost-btn text-xs py-2.5 px-3 disabled:opacity-40" title="Clear chat">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
              <button type="submit" disabled={!input.trim() || sendMutation.isPending}
                className="neon-btn py-2.5 px-4 disabled:opacity-40 disabled:cursor-not-allowed" aria-label="Send">
                {sendMutation.isPending ? <Spinner /> : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </div>
          </form>
          <p className={`text-center text-[11px] mt-2 ${isDark ? 'text-white/20' : 'text-gray-400'}`}>
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
          40% { transform: translateY(-5px); opacity: 1; }
        }
      `}</style>
    </Layout>
  )
}
