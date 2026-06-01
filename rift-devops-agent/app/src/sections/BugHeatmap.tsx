import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Fix } from '@/types';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';

interface BugHeatmapProps {
  fixes: Fix[];
}

interface HeatmapData {
  path: string;
  error_count: number;
  fix_count: number;
  file_count: number;
}

export function BugHeatmap({ fixes }: BugHeatmapProps) {
  const heatmapData = useMemo(() => {
    const data: Record<string, HeatmapData> = {};

    fixes.forEach(fix => {
      const parts = fix.file_path.split('/');
      const directory = parts.length > 1 ? parts[0] : 'root';

      if (!data[directory]) {
        data[directory] = {
          path: directory,
          error_count: 0,
          fix_count: 0,
          file_count: 0,
        };
      }

      data[directory].error_count += 1;
      data[directory].file_count += 1;

      if (fix.status === 'verified') {
        data[directory].fix_count += 1;
      }
    });

    return Object.values(data).sort((a, b) => b.error_count - a.error_count);
  }, [fixes]);

  const getIntensityColor = (count: number, max: number) => {
    const intensity = count / max;
    if (intensity > 0.75) return '#ef4444'; // Red
    if (intensity > 0.5) return '#f97316';  // Orange
    if (intensity > 0.25) return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  const maxErrors = Math.max(...heatmapData.map(d => d.error_count), 1);

  if (heatmapData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Bug Heatmap</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No bug data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Bug Heatmap</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Bar Chart */}
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={heatmapData} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis 
                dataKey="path" 
                type="category" 
                tick={{ fontSize: 12 }}
                width={100}
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload as HeatmapData;
                    return (
                      <div className="bg-card border rounded-lg p-3 shadow-lg">
                        <div className="font-medium">{data.path}</div>
                        <div className="text-sm text-muted-foreground">
                          Errors: {data.error_count}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Fixed: {data.fix_count}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Files: {data.file_count}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="error_count" radius={[0, 4, 4, 0]}>
                {heatmapData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={getIntensityColor(entry.error_count, maxErrors)} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Heatmap Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {heatmapData.map((item) => (
            <div
              key={item.path}
              className="p-4 rounded-lg border"
              style={{
                backgroundColor: `${getIntensityColor(item.error_count, maxErrors)}20`,
                borderColor: getIntensityColor(item.error_count, maxErrors),
              }}
            >
              <div className="font-medium truncate">{item.path}</div>
              <div className="text-2xl font-bold mt-1">
                {item.error_count}
              </div>
              <div className="text-xs text-muted-foreground">
                {item.fix_count} fixed
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500" />
            <span>Low</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-500" />
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-orange-500" />
            <span>High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-500" />
            <span>Critical</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
