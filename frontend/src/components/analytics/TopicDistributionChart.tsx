import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'

interface TopicDistributionChartProps {
  difficultyMap: Record<number, number>
}

export default function TopicDistributionChart({ difficultyMap }: TopicDistributionChartProps) {
  if (!difficultyMap || Object.keys(difficultyMap).length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500 text-sm border border-dashed border-gray-800 rounded-xl">
        No solved difficulty distribution available.
      </div>
    )
  }

  const data = Object.entries(difficultyMap)
    .map(([rating, count]) => ({
      rating: parseInt(rating, 10),
      count: count,
    }))
    .sort((a, b) => a.rating - b.rating)

  return (
    <div className="bg-[#111827] border border-gray-800 p-5 rounded-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white text-base">Difficulty Spectrum</h3>
          <p className="text-xs text-gray-400">Solved problem counts grouped by rating</p>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis dataKey="rating" stroke="#6B7280" tick={{ fontSize: 11 }} />
            <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                borderColor: '#374151',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '12px',
              }}
              formatter={(value: any) => [`${value} Problems`, 'Solved']}
              labelFormatter={(rating) => `Difficulty Rating: ${rating}`}
            />
            <Bar dataKey="count" fill="#06B6D4" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
