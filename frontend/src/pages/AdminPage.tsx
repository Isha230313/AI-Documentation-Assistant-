import { useState, useRef, type DragEvent, type ChangeEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { ingestFiles, ingestUrls } from '../api/ingest'
import { getCollections } from '../api/collections'
import { getSources, deleteSource } from '../api/sources'
import Layout from '../components/Layout'
import Spinner from '../components/Spinner'
import type { IngestResponse } from '../types'

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const ACCEPTED_TYPES = ['.pdf', '.docx', '.txt']
const ACCEPTED_MIME = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
]

// ─── File Upload Section ──────────────────────────────────────────────────────

function FileUploadSection() {
  const [files, setFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dragOver, setDragOver] = useState(false)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: () => ingestFiles(files, (pct) => setUploadProgress(pct)),
    onSuccess: (data: IngestResponse) => {
      setSuccessMsg(`${data.message} — ${data.chunks_added} chunks added.`)
      setErrorMsg(null)
      setFiles([])
      setUploadProgress(0)
      queryClient.invalidateQueries({ queryKey: ['collections'] })
    },
    onError: (error: unknown) => {
      setErrorMsg(error instanceof AxiosError
        ? (error.response?.data?.detail ?? 'Upload failed. Please try again.')
        : 'An unexpected error occurred.')
      setUploadProgress(0)
    },
  })

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return
    const valid = Array.from(incoming).filter((f) => ACCEPTED_MIME.includes(f.type))
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name + f.size))
      return [...prev, ...valid.filter((f) => !existing.has(f.name + f.size))]
    })
    setSuccessMsg(null)
    setErrorMsg(null)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    addFiles(e.dataTransfer.files)
  }

  const removeFile = (name: string) => setFiles((prev) => prev.filter((f) => f.name !== name))

  const isUploading = uploadMutation.isPending

  return (
    <section className="glass-card p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
          style={{ background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.3)' }}>
          📄
        </div>
        <div>
          <h2 className="font-semibold text-gray-900 dark:text-white">Upload Documents</h2>
          <p className="text-xs text-gray-500 dark:text-white/40">PDF, DOCX, or TXT files</p>
        </div>
      </div>

      <div
        onClick={() => !isUploading && inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onKeyDown={(e) => e.key === 'Enter' && !isUploading && inputRef.current?.click()}
        role="button" tabIndex={0}
        className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 focus:outline-none"
        style={{
          borderColor: dragOver ? 'rgba(59,130,246,0.8)' : 'rgba(59,130,246,0.25)',
          background: dragOver ? 'rgba(59,130,246,0.1)' : 'rgba(59,130,246,0.04)',
        }}
      >
        <input ref={inputRef} type="file" multiple accept={ACCEPTED_TYPES.join(',')}
          onChange={(e: ChangeEvent<HTMLInputElement>) => addFiles(e.target.files)}
          className="hidden" disabled={isUploading} />
        <div className="text-4xl mb-3">{dragOver ? '📂' : '📁'}</div>
        <p className="text-gray-700 dark:text-white/70 font-medium text-sm">
          {dragOver ? 'Drop files here' : 'Drag & drop or click to browse'}
        </p>
        <p className="text-gray-500 dark:text-white/40 text-xs mt-1">
          Accepted: {ACCEPTED_TYPES.join(', ')} · Multiple files supported
        </p>
      </div>

      {files.length > 0 && (
        <ul className="space-y-2 animate-fade-in">
          {files.map((file) => (
            <li key={file.name + file.size}
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl"
              style={{ background: 'rgba(59,130,246,0.04)', border: '1px solid rgba(0,0,0,0.06)' }}>
              <span className="text-lg shrink-0">
                {file.type === 'application/pdf' ? '📕' : file.type.includes('word') ? '📘' : '📄'}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800 dark:text-white/80 truncate font-medium">{file.name}</p>
                <p className="text-xs text-gray-500 dark:text-white/40">{formatBytes(file.size)}</p>
              </div>
              {!isUploading && (
                <button onClick={(e) => { e.stopPropagation(); removeFile(file.name) }}
                  className="text-gray-300 dark:text-white/20 hover:text-red-400 transition-colors text-lg leading-none ml-1"
                  aria-label={`Remove ${file.name}`}>×</button>
              )}
            </li>
          ))}
        </ul>
      )}

      {isUploading && uploadProgress > 0 && (
        <div className="space-y-1.5 animate-fade-in">
          <div className="flex justify-between text-xs text-gray-500 dark:text-white/40">
            <span>Uploading…</span><span>{uploadProgress}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-gray-200 dark:bg-white/10 overflow-hidden">
            <div className="h-full rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%`, background: 'linear-gradient(90deg, #3b82f6, #06b6d4)' }} />
          </div>
        </div>
      )}

      {successMsg && <div className="success-banner animate-fade-in" role="status"><span>✓</span><span>{successMsg}</span></div>}
      {errorMsg && <div className="error-banner animate-fade-in" role="alert"><span>{errorMsg}</span></div>}

      <button onClick={() => uploadMutation.mutate()} disabled={files.length === 0 || isUploading}
        className="neon-btn w-full justify-center py-3 disabled:opacity-40 disabled:cursor-not-allowed">
        {isUploading ? (
          <><Spinner /><span>Uploading {files.length} file{files.length !== 1 ? 's' : ''}…</span></>
        ) : (
          <span>Upload {files.length > 0 ? `${files.length} file${files.length !== 1 ? 's' : ''}` : 'Files'}</span>
        )}
      </button>
    </section>
  )
}

// ─── URL Ingest Section ───────────────────────────────────────────────────────

function UrlIngestSection() {
  const [urlText, setUrlText] = useState('')
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const ingestMutation = useMutation({
    mutationFn: (urls: string[]) => ingestUrls({ urls }),
    onSuccess: (data: IngestResponse) => {
      setSuccessMsg(`${data.message} — ${data.chunks_added} chunks added.`)
      setErrorMsg(null)
      setUrlText('')
      queryClient.invalidateQueries({ queryKey: ['collections'] })
    },
    onError: (error: unknown) => {
      setErrorMsg(error instanceof AxiosError
        ? (error.response?.data?.detail ?? 'Ingest failed. Please try again.')
        : 'An unexpected error occurred.')
    },
  })

  const parseUrls = () =>
    urlText.split('\n').map((u) => u.trim()).filter((u) => /^https?:\/\//.test(u))

  const handleIngest = () => {
    const urls = parseUrls()
    if (urls.length === 0) {
      setErrorMsg('No valid URLs found. Each URL must start with http:// or https://.')
      return
    }
    setSuccessMsg(null)
    setErrorMsg(null)
    ingestMutation.mutate(urls)
  }

  const validUrlCount = parseUrls().length
  const isLoading = ingestMutation.isPending

  return (
    <section className="glass-card p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
          style={{ background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.3)' }}>
          🌐
        </div>
        <div>
          <h2 className="font-semibold text-gray-900 dark:text-white">Ingest URLs</h2>
          <p className="text-xs text-gray-500 dark:text-white/40">One URL per line · http(s) only</p>
        </div>
      </div>

      <div className="relative">
        <textarea
          value={urlText}
          onChange={(e) => { setUrlText(e.target.value); setSuccessMsg(null); setErrorMsg(null) }}
          placeholder={'https://docs.example.com/getting-started\nhttps://docs.example.com/api-reference'}
          rows={6} disabled={isLoading}
          className="input-field resize-none font-mono text-xs leading-relaxed scrollbar-thin"
        />
        {validUrlCount > 0 && (
          <span className="absolute bottom-3 right-3 text-[11px] px-2 py-0.5 rounded-full"
            style={{ background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(59,130,246,0.3)', color: '#3b82f6' }}>
            {validUrlCount} URL{validUrlCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {successMsg && <div className="success-banner animate-fade-in" role="status"><span>✓</span><span>{successMsg}</span></div>}
      {errorMsg && <div className="error-banner animate-fade-in" role="alert"><span>{errorMsg}</span></div>}

      <button onClick={handleIngest} disabled={validUrlCount === 0 || isLoading}
        className="neon-btn w-full justify-center py-3 disabled:opacity-40 disabled:cursor-not-allowed">
        {isLoading
          ? <><Spinner /><span>Ingesting URLs…</span></>
          : <span>Ingest {validUrlCount > 0 ? `${validUrlCount} URL${validUrlCount !== 1 ? 's' : ''}` : 'URLs'}</span>}
      </button>
    </section>
  )
}

// ─── Collection Stats ─────────────────────────────────────────────────────────

function CollectionStats() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['collections'],
    queryFn: getCollections,
    refetchInterval: 30_000,
  })

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2"><span>📊</span> Collection Stats</h2>
        <button onClick={() => refetch()} disabled={isLoading} className="ghost-btn text-xs py-1.5 px-3">
          {isLoading ? <Spinner size={3} /> : (
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          )}
          <span>Refresh</span>
        </button>
      </div>

      {isError && <div className="error-banner" role="alert"><span>Failed to load collection statistics.</span></div>}

      {isLoading && !data && (
        <div className="grid grid-cols-2 gap-4">
          {[1, 2].map((i) => <div key={i} className="glass-card p-5 animate-pulse" style={{ height: '88px' }} />)}
        </div>
      )}

      {data && (
        <>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: 'Total Vectors', value: data.total_vectors.toLocaleString(), icon: '🔢', accent: '#3b82f6' },
              { label: 'Collections',   value: data.total_collections,              icon: '🗂️', accent: '#06b6d4' },
            ].map(({ label, value, icon, accent }) => (
              <div key={label} className="glass-card p-5 flex items-center gap-4" style={{ borderColor: `${accent}30` }}>
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0"
                  style={{ background: `${accent}15`, border: `1px solid ${accent}30` }}>{icon}</div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-white/40 uppercase tracking-widest font-medium">{label}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-0.5">{value}</p>
                </div>
              </div>
            ))}
          </div>

          {data.collections.length > 0 && (
            <div className="glass-card p-4 space-y-2 animate-fade-in">
              <p className="text-xs text-gray-500 dark:text-white/40 uppercase tracking-widest font-medium mb-3">Individual Collections</p>
              {data.collections.map((col) => (
                <div key={col.name} className="flex items-center justify-between py-2 px-3 rounded-lg"
                  style={{ background: 'rgba(0,0,0,0.02)' }}>
                  <span className="text-sm text-gray-700 dark:text-white/70 font-medium truncate">{col.name}</span>
                  <span className="text-xs font-semibold shrink-0 ml-2 px-2 py-0.5 rounded-full"
                    style={{ background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.25)', color: '#3b82f6' }}>
                    {col.vectors.toLocaleString()} vectors
                  </span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}

// ─── Indexed Sources ──────────────────────────────────────────────────────────

function IndexedSources() {
  const queryClient = useQueryClient()
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

  const { data: sources = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['sources'],
    queryFn: getSources,
  })

  const deleteMutation = useMutation({
    mutationFn: (source: string) => deleteSource(source),
    onSuccess: () => {
      setConfirmDelete(null)
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      queryClient.invalidateQueries({ queryKey: ['collections'] })
    },
  })

  return (
    <section className="glass-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
            style={{ background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.3)' }}>
            🗂️
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 dark:text-white">Indexed Sources</h2>
            <p className="text-xs text-gray-500 dark:text-white/40">{sources.length} source{sources.length !== 1 ? 's' : ''} in the knowledge base</p>
          </div>
        </div>
        <button onClick={() => refetch()} disabled={isLoading} className="ghost-btn text-xs py-1.5 px-3">
          {isLoading ? <Spinner size={3} /> : (
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          )}
          <span>Refresh</span>
        </button>
      </div>

      {isError && <div className="error-banner" role="alert"><span>Failed to load sources.</span></div>}

      {!isLoading && sources.length === 0 && (
        <p className="text-gray-500 dark:text-white/40 text-sm text-center py-6">No documents indexed yet.</p>
      )}

      {sources.length > 0 && (
        <ul className="space-y-2">
          {sources.map((src) => (
            <li key={src} className="flex items-center justify-between gap-3 px-4 py-3 rounded-xl"
              style={{ background: 'rgba(59,130,246,0.04)', border: '1px solid rgba(0,0,0,0.06)' }}>
              <span className="text-sm text-gray-700 dark:text-white/70 truncate flex-1" title={src}>
                {src.startsWith('http') ? '🌐' : '📄'} {src}
              </span>

              {confirmDelete === src ? (
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs text-gray-500 dark:text-white/40">Delete?</span>
                  <button onClick={() => deleteMutation.mutate(src)} disabled={deleteMutation.isPending}
                    className="text-xs px-2 py-1 rounded-lg text-red-400 border border-red-500/30 hover:bg-red-500/10 transition-colors disabled:opacity-40">
                    {deleteMutation.isPending ? <Spinner size={3} /> : 'Yes'}
                  </button>
                  <button onClick={() => setConfirmDelete(null)}
                    className="text-xs px-2 py-1 rounded-lg text-gray-500 dark:text-white/40 border border-gray-200 dark:border-white/10 hover:bg-gray-100 dark:hover:bg-white/5 transition-colors">
                    No
                  </button>
                </div>
              ) : (
                <button onClick={() => setConfirmDelete(src)}
                  className="shrink-0 text-gray-300 dark:text-white/20 hover:text-red-400 transition-colors text-lg leading-none"
                  aria-label={`Delete ${src}`}>
                  ×
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

// ─── Admin Page ───────────────────────────────────────────────────────────────

export default function AdminPage() {
  return (
    <Layout>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-4xl mx-auto w-full px-4 py-8 space-y-8">
          <div className="animate-fade-in">
            <h1 className="text-2xl font-bold text-gradient">Admin Panel</h1>
            <p className="text-gray-500 dark:text-white/40 text-sm mt-1">Manage your knowledge base — upload documents or ingest URLs.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6 animate-slide-up">
            <FileUploadSection />
            <UrlIngestSection />
          </div>
          <div className="animate-fade-in">
            <IndexedSources />
          </div>
          <div className="animate-fade-in">
            <CollectionStats />
          </div>
        </div>
      </div>
    </Layout>
  )
}
