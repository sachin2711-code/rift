// import { Trophy, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Progress } from '@/components/ui/progress';
// import type { ScoreBreakdown } from '@/types';
// import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// interface ScoreBreakdownPanelProps {
//   score: ScoreBreakdown;
// }

// export function ScoreBreakdownPanel({ score }: ScoreBreakdownPanelProps) {
//   const chartData = [
//     { name: 'Base', value: score.base_score, color: '#3b82f6' },
//     { name: 'Speed', value: score.speed_bonus, color: '#22c55e' },
//     { name: 'Efficiency', value: -score.efficiency_penalty, color: '#ef4444' },
//     { name: 'Success', value: score.success_bonus, color: '#8b5cf6' },
//   ];

//   const getScoreColor = (total: number) => {
//     if (total >= 120) return 'text-green-500';
//     if (total >= 100) return 'text-blue-500';
//     if (total >= 80) return 'text-yellow-500';
//     return 'text-red-500';
//   };

//   return (
//     <Card>
//       <CardHeader>
//         <CardTitle className="flex items-center gap-2">
//           <Trophy className="h-5 w-5" />
//           Score Breakdown
//         </CardTitle>
//       </CardHeader>
//       <CardContent className="space-y-6">
//         {/* Total Score */}
//         <div className="text-center">
//           <div className={`text-5xl font-bold ${getScoreColor(score.total_score)}`}>
//             {score.total_score}
//           </div>
//           <div className="text-sm text-muted-foreground mt-1">Total Score</div>
//         </div>

//         {/* Score Components */}
//         <div className="space-y-3">
//           {/* Base Score */}
//           <div className="space-y-1">
//             <div className="flex justify-between text-sm">
//               <span className="flex items-center gap-1">
//                 <Trophy className="h-3 w-3" />
//                 Base Score
//               </span>
//               <span className="font-medium">{score.base_score}</span>
//             </div>
//             <Progress value={100} className="h-2" />
//           </div>

//           {/* Speed Bonus */}
//           <div className="space-y-1">
//             <div className="flex justify-between text-sm">
//               <span className="flex items-center gap-1">
//                 <Zap className="h-3 w-3" />
//                 Speed Bonus
//               </span>
//               <span className="font-medium text-green-500">+{score.speed_bonus}</span>
//             </div>
//             <Progress 
//               value={score.speed_bonus > 0 ? 100 : 0} 
//               className="h-2 bg-muted"
//             />
//           </div>

//           {/* Efficiency Penalty */}
//           <div className="space-y-1">
//             <div className="flex justify-between text-sm">
//               <span className="flex items-center gap-1">
//                 <AlertTriangle className="h-3 w-3" />
//                 Efficiency Penalty
//               </span>
//               <span className="font-medium text-red-500">-{score.efficiency_penalty}</span>
//             </div>
//             <Progress 
//               value={score.efficiency_penalty > 0 ? 100 : 0} 
//               className="h-2 bg-muted"
//             />
//           </div>

//           {/* Success Bonus */}
//           <div className="space-y-1">
//             <div className="flex justify-between text-sm">
//               <span className="flex items-center gap-1">
//                 <CheckCircle2 className="h-3 w-3" />
//                 Success Bonus
//               </span>
//               <span className="font-medium text-purple-500">+{score.success_bonus}</span>
//             </div>
//             <Progress 
//               value={score.success_bonus > 0 ? 100 : 0} 
//               className="h-2 bg-muted"
//             />
//           </div>
//         </div>

//         {/* Chart */}
//         <div className="h-48">
//           <ResponsiveContainer width="100%" height="100%">
//             <BarChart data={chartData}>
//               <XAxis dataKey="name" tick={{ fontSize: 12 }} />
//               <YAxis tick={{ fontSize: 12 }} />
//               <Tooltip 
//                 formatter={(value: number) => [value, 'Points']}
//                 contentStyle={{ borderRadius: 8 }}
//               />
//               <Bar dataKey="value" radius={[4, 4, 0, 0]}>
//                 {chartData.map((entry, index) => (
//                   <Cell key={`cell-${index}`} fill={entry.color} />
//                 ))}
//               </Bar>
//             </BarChart>
//           </ResponsiveContainer>
//         </div>

//         {/* Time Taken */}
//         <div className="text-center text-sm text-muted-foreground">
//           Time taken: {(score.time_taken_seconds / 60).toFixed(1)} minutes
//         </div>
//       </CardContent>
//     </Card>
//   );
// }
import { Trophy, Zap, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { ScoreBreakdown } from '@/types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ScoreBreakdownPanelProps {
  score: ScoreBreakdown | null | undefined;
}

export function ScoreBreakdownPanel({ score }: ScoreBreakdownPanelProps) {
  // ✅ Show placeholder while score is not yet available (before CI/CD completes)
  if (!score) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Score Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-3">
            <Clock className="h-8 w-8 animate-pulse" />
            <p className="text-sm font-medium">Score will appear after CI/CD completes</p>
            <p className="text-xs opacity-60">Final score is calculated at the end of the run</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = [
    { name: 'Base', value: score.base_score, color: '#3b82f6' },
    { name: 'Speed', value: score.speed_bonus, color: '#22c55e' },
    { name: 'Efficiency', value: -score.efficiency_penalty, color: '#ef4444' },
    { name: 'Success', value: score.success_bonus, color: '#8b5cf6' },
  ];

  const getScoreColor = (total: number) => {
    if (total >= 120) return 'text-green-500';
    if (total >= 100) return 'text-blue-500';
    if (total >= 80) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5" />
          Score Breakdown
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Total Score */}
        <div className="text-center">
          <div className={`text-5xl font-bold ${getScoreColor(score.total_score)}`}>
            {score.total_score}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Total Score</div>
        </div>

        {/* Score Components */}
        <div className="space-y-3">
          {/* Base Score */}
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="flex items-center gap-1">
                <Trophy className="h-3 w-3" />
                Base Score
              </span>
              <span className="font-medium">{score.base_score}</span>
            </div>
            <Progress value={100} className="h-2" />
          </div>

          {/* Speed Bonus */}
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="flex items-center gap-1">
                <Zap className="h-3 w-3" />
                Speed Bonus
              </span>
              <span className="font-medium text-green-500">+{score.speed_bonus}</span>
            </div>
            <Progress
              value={score.speed_bonus > 0 ? 100 : 0}
              className="h-2 bg-muted"
            />
          </div>

          {/* Efficiency Penalty */}
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" />
                Efficiency Penalty
              </span>
              <span className="font-medium text-red-500">-{score.efficiency_penalty}</span>
            </div>
            <Progress
              value={score.efficiency_penalty > 0 ? 100 : 0}
              className="h-2 bg-muted"
            />
          </div>

          {/* Success Bonus */}
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Success Bonus
              </span>
              <span className="font-medium text-purple-500">+{score.success_bonus}</span>
            </div>
            <Progress
              value={score.success_bonus > 0 ? 100 : 0}
              className="h-2 bg-muted"
            />
          </div>
        </div>

        {/* Chart */}
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(value: number) => [value, 'Points']}
                contentStyle={{ borderRadius: 8 }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Time Taken */}
        <div className="text-center text-sm text-muted-foreground">
          Time taken: {(score.time_taken_seconds / 60).toFixed(1)} minutes
        </div>
      </CardContent>
    </Card>
  );
}