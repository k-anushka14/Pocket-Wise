import { Pencil, Trash2 } from 'lucide-react'
import { formatCurrency, toLabel } from '../utils/constants'

const TYPE_BADGE = {
  need: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300',
  want: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
}

export default function TransactionTable({ transactions, onEdit, onDelete }) {
  return (
    <div className="overflow-x-auto rounded-2xl bg-white shadow-sm dark:bg-slate-900">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-500 dark:border-slate-800 dark:text-slate-400">
            <th className="px-4 py-3 font-medium">Date</th>
            <th className="px-4 py-3 font-medium">Description</th>
            <th className="px-4 py-3 font-medium">Category</th>
            <th className="px-4 py-3 font-medium">Payment</th>
            <th className="px-4 py-3 font-medium">Type</th>
            <th className="px-4 py-3 text-right font-medium">Amount</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn) => (
            <tr
              key={txn.id}
              className="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50"
            >
              <td className="whitespace-nowrap px-4 py-3 text-slate-600 dark:text-slate-300">{txn.date}</td>
              <td className="px-4 py-3 text-slate-900 dark:text-white">{txn.description || '—'}</td>
              <td className="px-4 py-3 text-slate-600 dark:text-slate-300">{toLabel(txn.category)}</td>
              <td className="px-4 py-3 text-slate-600 dark:text-slate-300">{toLabel(txn.payment_method)}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${TYPE_BADGE[txn.type]}`}>
                  {toLabel(txn.type)}
                </span>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-right font-medium text-slate-900 dark:text-white">
                {formatCurrency(txn.amount)}
              </td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => onEdit(txn)}
                    className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                    aria-label="Edit"
                  >
                    <Pencil size={15} />
                  </button>
                  <button
                    onClick={() => onDelete(txn)}
                    className="text-slate-400 hover:text-red-600"
                    aria-label="Delete"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
