import { useState, useRef, useEffect } from 'react'
import { SendHorizonal, Bot, User } from 'lucide-react'
import { askAssistant } from '../api/ai'

const SUGGESTED_QUESTIONS = [
  'Where am I spending the most?',
  'How can I save ₹2,000 this month?',
  'Why am I running out of money before month end?',
  'What should I reduce to hit my savings goal?',
]

export default function AIAssistant() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(question) {
    const q = question || input.trim()
    if (!q) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text: q }])
    setLoading(true)
    try {
      const res = await askAssistant(q)
      setMessages((m) => [...m, {
        role: 'assistant',
        text: res.answer,
        ai_available: res.ai_available,
      }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', text: `Error: ${err.message}`, error: true }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col rounded-2xl bg-white shadow-sm dark:bg-slate-900">
      <div className="border-b border-slate-100 px-5 py-4 dark:border-slate-800">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-white">
          <Bot size={16} /> PocketWise Assistant
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">Ask anything about your finances</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 p-4">
        {messages.length === 0 && (
          <div className="space-y-2">
            <p className="text-xs text-slate-400 dark:text-slate-500">Try asking:</p>
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="block w-full rounded-xl bg-slate-50 px-4 py-2.5 text-left text-sm text-slate-600 hover:bg-slate-100 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-white ${
              msg.role === 'user' ? 'bg-slate-900 dark:bg-white' : 'bg-blue-600'
            }`}>
              {msg.role === 'user'
                ? <User size={13} className="dark:text-slate-900" />
                : <Bot size={13} />}
            </div>
            <div className={`max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm ${
              msg.role === 'user'
                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                : msg.error
                ? 'bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-300'
                : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200'
            }`}>
              {msg.text}
              {msg.ai_available === false && (
                <p className="mt-1 text-xs opacity-60">AI offline — using local data</p>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white">
              <Bot size={13} />
            </div>
            <div className="rounded-2xl bg-slate-100 px-3.5 py-2.5 dark:bg-slate-800">
              <span className="inline-flex gap-1 text-slate-400">
                <span className="animate-bounce">·</span>
                <span className="animate-bounce [animation-delay:150ms]">·</span>
                <span className="animate-bounce [animation-delay:300ms]">·</span>
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-slate-100 p-3 dark:border-slate-800">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
            placeholder="Ask about your spending…"
            className="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            disabled={loading}
          />
          <button
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="flex items-center justify-center rounded-xl bg-slate-900 px-3 py-2 text-white disabled:opacity-40 dark:bg-white dark:text-slate-900"
            aria-label="Send"
          >
            <SendHorizonal size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
