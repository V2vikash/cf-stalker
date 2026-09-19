import { BrainCircuit, ShieldAlert, Sparkles, ArrowRight } from 'lucide-react'

interface AICoachPanelProps {
  review?: {
    handle: string
    current_rating: number
    summary: string
    tactical_advice: string[]
    strengths_assessment: string[]
    weaknesses_assessment: string[]
    action_plan: Array<{
      step: number
      focus_area: string
      action: string
      target_problem_rating: number
    }>
  } | null
  isLoading?: boolean
  onGenerate?: () => void
}

export default function AICoachPanel({ review, isLoading, onGenerate }: AICoachPanelProps) {
  return (
    <div className="bg-[#111827] border border-indigo-500/30 p-6 rounded-2xl space-y-6 relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              AI Performance Coach
              <span className="text-xs bg-indigo-500/10 text-indigo-400 font-semibold px-2 py-0.5 rounded border border-indigo-500/20">
                LLM Structured Engine
              </span>
            </h3>
            <p className="text-xs text-gray-400">Personalized tactical coaching based on your actual Codeforces statistical payload</p>
          </div>
        </div>

        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium text-xs px-4 py-2 rounded-lg transition-all shadow-md shadow-indigo-500/20 disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {isLoading ? 'Generating Review...' : 'Generate Performance Audit'}
        </button>
      </div>

      {!review && !isLoading && (
        <div className="text-center py-10 text-gray-400 text-sm space-y-2">
          <p>Click "Generate Performance Audit" to trigger deep LLM statistical coaching.</p>
        </div>
      )}

      {review && (
        <div className="space-y-6">
          {/* Executive Summary */}
          <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 text-xs text-gray-300 leading-relaxed">
            <span className="font-semibold text-indigo-400 block mb-1">Executive Summary</span>
            {review.summary}
          </div>

          {/* Tactical Advice & Assessments Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Tactical Advice */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Tactical Recommendations</h4>
              <ul className="space-y-2">
                {review.tactical_advice.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-gray-300 bg-gray-900/40 p-2.5 rounded-lg border border-gray-800">
                    <ArrowRight className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Weakness Assessment */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Identified Deficits</h4>
              <ul className="space-y-2">
                {review.weaknesses_assessment.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-rose-300 bg-rose-950/20 p-2.5 rounded-lg border border-rose-500/20">
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* 3-Step Action Plan */}
          <div className="space-y-3 pt-4 border-t border-gray-800">
            <h4 className="text-sm font-bold text-white">Targeted 3-Step Action Plan</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {review.action_plan.map((step) => (
                <div key={step.step} className="bg-gray-900/80 border border-indigo-500/20 p-3.5 rounded-xl space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="w-6 h-6 rounded-full bg-indigo-600/30 text-indigo-300 font-bold text-xs flex items-center justify-center">
                      {step.step}
                    </span>
                    <span className="text-[10px] font-mono font-semibold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded">
                      {step.target_problem_rating} Rating
                    </span>
                  </div>
                  <p className="font-semibold text-xs text-white capitalize">{step.focus_area}</p>
                  <p className="text-[11px] text-gray-400 leading-snug">{step.action}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
