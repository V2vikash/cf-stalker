import { useState } from 'react'
import { 
  BarChart3, 
  BrainCircuit, 
  Compass, 
  Flame, 
  LayoutDashboard, 
  Search, 
  ShieldCheck, 
  Target, 
  Trophy, 
  Loader2,
  AlertCircle
} from 'lucide-react'

import { api } from './services/api'
import RatingChart from './components/analytics/RatingChart'
import TopicDistributionChart from './components/analytics/TopicDistributionChart'
import SkillGapMatrix from './components/skill_gap/SkillGapMatrix'
import RecommendationCards from './components/recommendations/RecommendationCards'
import AICoachPanel from './components/ai_coach/AICoachPanel'

export default function App() {
  const [handleInput, setHandleInput] = useState('')
  const [activeHandle, setActiveHandle] = useState('')
  const [activeTab, setActiveTab] = useState('dashboard')

  const [isSyncing, setIsSyncing] = useState(false)
  const [syncStatusText, setSyncStatusText] = useState('')
  const [errorMsg, setErrorMsg] = useState('')

  // State data
  const [overview, setOverview] = useState<any>(null)
  const [contests, setContests] = useState<any>(null)
  const [topics, setTopics] = useState<any>(null)
  const [skillGap, setSkillGap] = useState<any>(null)
  const [recommendations, setRecommendations] = useState<any>(null)
  const [aiReview, setAiReview] = useState<any>(null)
  const [isAiLoading, setIsAiLoading] = useState(false)

  const loadProfileData = async (handle: string) => {
    try {
      setErrorMsg('')
      const [ovData, cData, tData, sgData, recData] = await Promise.all([
        api.getOverview(handle).catch(() => null),
        api.getContests(handle).catch(() => null),
        api.getTopics(handle).catch(() => null),
        api.getSkillGap(handle).catch(() => null),
        api.getRecommendations(handle).catch(() => null),
      ])

      setOverview(ovData)
      setContests(cData)
      setTopics(tData)
      setSkillGap(sgData)
      setRecommendations(recData)
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed loading profile analytics')
    }
  }

  const handleAnalyze = async () => {
    const handle = handleInput.trim()
    if (!handle) return

    setIsSyncing(true)
    setErrorMsg('')
    setSyncStatusText('Initiating Codeforces Data Ingestion...')

    try {
      const syncRes = await api.syncProfile(handle)
      const jobId = syncRes.sync_job_id

      // Poll sync status
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await api.getSyncStatus(jobId)
          setSyncStatusText(`Sync Status: ${statusRes.status}`)

          if (statusRes.status === 'COMPLETED') {
            clearInterval(pollInterval)
            setIsSyncing(false)
            setActiveHandle(handle)
            await loadProfileData(handle)
          } else if (statusRes.status === 'FAILED') {
            clearInterval(pollInterval)
            setIsSyncing(false)
            setErrorMsg(statusRes.error_message || 'Sync task failed')
          }
        } catch (e) {
          clearInterval(pollInterval)
          setIsSyncing(false)
          setErrorMsg('Failed checking sync status')
        }
      }, 2000)
    } catch (err: any) {
      setIsSyncing(false)
      setErrorMsg(err.message || 'Failed initiating Codeforces sync')
    }
  }

  const handleGenerateAiReview = async () => {
    if (!activeHandle) return
    setIsAiLoading(true)
    try {
      const reviewData = await api.getAICoachReview(activeHandle)
      setAiReview(reviewData)
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed generating AI performance review')
    } finally {
      setIsAiLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-[#0B0F19] text-gray-100 overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#111827] border-r border-gray-800 flex flex-col justify-between p-4">
        <div>
          <div className="flex items-center gap-3 px-2 py-4 mb-6 border-b border-gray-800">
            <img 
              src="/assets/logo.jpg" 
              alt="CF Stalker Logo" 
              className="w-10 h-10 rounded-xl object-cover shadow-lg shadow-cyan-500/20 border border-cyan-500/30 shrink-0" 
            />
            <div>
              <h1 className="font-bold text-lg text-white leading-tight">CF Stalker</h1>
              <p className="text-xs text-indigo-400 font-medium">CP Intelligence Engine</p>
            </div>
          </div>

          <nav className="space-y-1">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'analytics', label: 'Rating & Contests', icon: BarChart3 },
              { id: 'skill-gap', label: 'Skill Gap Matrix', icon: Target },
              { id: 'recommendations', label: 'Recommended Problems', icon: Compass },
              { id: 'ai-coach', label: 'AI Performance Coach', icon: BrainCircuit },
            ].map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                      : 'text-gray-400 hover:bg-gray-800/60 hover:text-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-3 bg-gray-900/60 rounded-xl border border-gray-800/80 text-xs text-gray-400">
          <div className="flex items-center gap-2 mb-1 text-emerald-400 font-semibold">
            <ShieldCheck className="w-4 h-4" /> System Online
          </div>
          <p>PostgreSQL 16 & Redis Celery pipeline initialized.</p>
        </div>
      </aside>

      {/* Main Content View */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        {/* Top Header */}
        <header className="h-16 bg-[#111827]/80 backdrop-blur border-b border-gray-800 px-6 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3 w-96 bg-gray-900/90 border border-gray-800 rounded-lg px-3 py-1.5 focus-within:border-indigo-500 transition-colors">
            <Search className="w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Enter Codeforces Handle (e.g. tourist)..."
              value={handleInput}
              onChange={(e) => setHandleInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              className="bg-transparent border-none text-sm text-gray-200 focus:outline-none w-full"
            />
            <button
              onClick={handleAnalyze}
              disabled={isSyncing}
              className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1 rounded transition-colors disabled:opacity-50 flex items-center gap-1"
            >
              {isSyncing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Analyze'}
            </button>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <span className="flex items-center gap-1 text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded-full border border-amber-400/20">
              <Flame className="w-3.5 h-3.5" /> Rate Limiter: Active
            </span>
            <span className="flex items-center gap-1 text-cyan-400 bg-cyan-400/10 px-2.5 py-1 rounded-full border border-cyan-400/20">
              <Trophy className="w-3.5 h-3.5" /> Codeforces REST v2
            </span>
          </div>
        </header>

        {/* Dashboard Content Container */}
        <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
          {/* Status / Error Banner */}
          {isSyncing && (
            <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-indigo-300 text-xs flex items-center gap-3 animate-pulse">
              <Loader2 className="w-4 h-4 animate-spin shrink-0" />
              <span>{syncStatusText}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl space-y-1">
              <p className="text-xs font-medium text-gray-400">Codeforces Handle</p>
              <p className="text-xl font-bold text-indigo-400">{activeHandle || 'Not Selected'}</p>
              <p className="text-[10px] text-gray-500">Active Profile</p>
            </div>
            <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl space-y-1">
              <p className="text-xs font-medium text-gray-400">Current Rating</p>
              <p className="text-xl font-bold text-amber-400">{overview?.current_rating || '----'}</p>
              <p className="text-[10px] text-gray-500">Max: {overview?.max_rating || '----'}</p>
            </div>
            <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl space-y-1">
              <p className="text-xs font-medium text-gray-400">Rating Volatility</p>
              <p className="text-xl font-bold text-emerald-400">{overview ? overview.volatility : '----'}</p>
              <p className="text-[10px] text-gray-500">Standard Deviation</p>
            </div>
            <div className="bg-[#111827] border border-gray-800 p-4 rounded-xl space-y-1">
              <p className="text-xs font-medium text-gray-400">Accuracy Ratio</p>
              <p className="text-xl font-bold text-cyan-400">{overview ? `${overview.overall_accuracy}%` : '----'}</p>
              <p className="text-[10px] text-gray-500">Solved: {overview?.total_solved || 0}</p>
            </div>
          </div>

          {/* Tab Views */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <RatingChart contests={contests?.contests || []} />
              <SkillGapMatrix gaps={skillGap?.gaps || []} />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <RatingChart contests={contests?.contests || []} />
              <TopicDistributionChart difficultyMap={topics?.difficulty_distribution || {}} />
            </div>
          )}

          {activeTab === 'skill-gap' && (
            <SkillGapMatrix gaps={skillGap?.gaps || []} />
          )}

          {activeTab === 'recommendations' && (
            <RecommendationCards recommendations={recommendations?.recommendations || []} />
          )}

          {activeTab === 'ai-coach' && (
            <AICoachPanel
              review={aiReview}
              isLoading={isAiLoading}
              onGenerate={handleGenerateAiReview}
            />
          )}
        </div>
      </main>
    </div>
  )
}
