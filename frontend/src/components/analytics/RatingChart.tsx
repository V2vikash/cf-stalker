import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts'

interface RatingChartProps {
  contests: Array<{
    contest_id: number
    name: string
    rank: number
    old_rating: number
    new_rating: number
    rating_change: number
  }>
}

export default function RatingChart({ contests }: RatingChartProps) {
  if (!contests || contests.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500 text-sm border border-dashed border-gray-800 rounded-xl">
        No contest rating history available.
      </div>
    )
  }

  const data = contests.map((c, idx) => ({
    index: idx + 1,
    name: c.name.length > 20 ? c.name.substring(0, 18) + '...' : c.name,
    fullName: c.name,
    rating: c.new_rating,
    delta: c.rating_change,
    rank: c.rank,
  }))

  return (
    <div className="bg-[#111827] border border-gray-800 p-5 rounded-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white text-base">Rating Trajectory</h3>
          <p className="text-xs text-gray-400">Progression across official Codeforces contests</p>
        </div>
        <div className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-md border border-indigo-500/20">
          {contests.length} Contests Evaluated
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis dataKey="index" stroke="#6B7280" tick={{ fontSize: 12 }} />
            <YAxis domain={['dataMin - 100', 'dataMax + 100']} stroke="#6B7280" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                borderColor: '#374151',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '12px',
              }}
              formatter={(value: any, _name: any, item: any) => [
                `${value} (${item.payload.delta >= 0 ? '+' : ''}${item.payload.delta})`,
                'New Rating',
              ]}
              labelFormatter={(label) => `Contest #${label}: ${data[Number(label) - 1]?.fullName || ''}`}
            />
            <ReferenceLine y={1200} stroke="#4B5563" strokeDasharray="3 3" label={{ value: 'Pupil', fill: '#9CA3AF', fontSize: 10 }} />
            <ReferenceLine y={1400} stroke="#10B981" strokeDasharray="3 3" label={{ value: 'Specialist', fill: '#10B981', fontSize: 10 }} />
            <ReferenceLine y={1600} stroke="#06B6D4" strokeDasharray="3 3" label={{ value: 'Expert', fill: '#06B6D4', fontSize: 10 }} />
            <ReferenceLine y={1900} stroke="#6366F1" strokeDasharray="3 3" label={{ value: 'Candidate Master', fill: '#6366F1', fontSize: 10 }} />
            <Line
              type="monotone"
              dataKey="rating"
              stroke="#818CF8"
              strokeWidth={3}
              dot={{ fill: '#4F46E5', r: 4 }}
              activeDot={{ r: 6, fill: '#6366F1' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
