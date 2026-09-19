import { Target, AlertTriangle, CheckCircle2, MinusCircle } from 'lucide-react'

interface SkillGapMatrixProps {
  gaps: Array<{
    tag: string
    user_rating: number
    tag_effective_rating: number
    gap_delta: number
    classification: string
  }>
}

export default function SkillGapMatrix({ gaps }: SkillGapMatrixProps) {
  if (!gaps || gaps.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-500 text-sm border border-dashed border-gray-800 rounded-xl">
        Skill gap data pending analysis.
      </div>
    )
  }

  return (
    <div className="bg-[#111827] border border-gray-800 p-5 rounded-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white text-base flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-400" /> Statistical Skill Gap Matrix
          </h3>
          <p className="text-xs text-gray-400">Classified topic rating gaps relative to overall rating</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {gaps.map((item, idx) => {
          const isWeak = item.classification === 'WEAKNESS'
          const isStrong = item.classification === 'STRENGTH'

          return (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border transition-all ${
                isWeak
                  ? 'bg-rose-950/20 border-rose-500/30 text-rose-200'
                  : isStrong
                  ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200'
                  : 'bg-gray-900/40 border-gray-800 text-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm capitalize">{item.tag}</span>
                {isWeak && <AlertTriangle className="w-4 h-4 text-rose-400" />}
                {isStrong && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                {!isWeak && !isStrong && <MinusCircle className="w-4 h-4 text-gray-500" />}
              </div>

              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-gray-400">Tag Level: {item.tag_effective_rating}</span>
                <span
                  className={`font-semibold ${
                    item.gap_delta > 0 ? 'text-rose-400' : 'text-emerald-400'
                  }`}
                >
                  {item.gap_delta > 0 ? `+${item.gap_delta} Gap` : `${item.gap_delta} Lead`}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
