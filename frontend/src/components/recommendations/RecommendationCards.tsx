import { ExternalLink, Compass } from 'lucide-react'

interface RecommendationCardsProps {
  recommendations: Array<{
    problem_id: string
    contest_id: number
    index: string
    name: string
    rating: number
    recommendation_type: string
    reason: string
    tags: string[]
  }>
}

export default function RecommendationCards({ recommendations }: RecommendationCardsProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-500 text-sm border border-dashed border-gray-800 rounded-xl">
        No problem recommendations generated yet. Analyze a profile first.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white text-base flex items-center gap-2">
            <Compass className="w-5 h-5 text-cyan-400" /> Algorithmic Problem Drills
          </h3>
          <p className="text-xs text-gray-400">Tailored practice problems categorized by learning objectives</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((item, idx) => {
          const isWeakDrill = item.recommendation_type === 'WEAK_TAG_DRILL'
          const cfUrl = `https://codeforces.com/problemset/problem/${item.contest_id}/${item.index}`

          return (
            <div
              key={idx}
              className="bg-[#111827] border border-gray-800 hover:border-indigo-500/40 p-4 rounded-xl flex flex-col justify-between space-y-3 transition-all group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span
                    className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${
                      isWeakDrill
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                    }`}
                  >
                    {isWeakDrill ? 'Weakness Drill' : 'Sweet Spot'}
                  </span>
                  <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                    {item.rating || 'Unrated'}
                  </span>
                </div>

                <a
                  href={cfUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-white group-hover:text-indigo-400 flex items-center gap-1.5 transition-colors"
                >
                  {item.contest_id}{item.index} — {item.name}
                  <ExternalLink className="w-3.5 h-3.5 opacity-60" />
                </a>

                <p className="text-xs text-gray-400 mt-1 leading-relaxed">{item.reason}</p>
              </div>

              <div className="flex flex-wrap gap-1.5 pt-2 border-t border-gray-800/60">
                {item.tags.map((t, tIdx) => (
                  <span key={tIdx} className="text-[10px] bg-gray-900 text-gray-400 px-2 py-0.5 rounded">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
