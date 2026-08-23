import Layout from '../components/Layout'
import AIAssistant from '../components/AIAssistant'

export default function Assistant() {
  return (
    <Layout>
      <div className="mb-4">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">AI Assistant</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Ask anything about your spending, savings, or budget.
        </p>
      </div>
      <div style={{ height: 'calc(100vh - 180px)' }}>
        <AIAssistant />
      </div>
    </Layout>
  )
}
