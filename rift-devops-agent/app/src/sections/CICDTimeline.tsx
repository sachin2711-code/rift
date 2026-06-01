import { CheckCircle2, XCircle, Clock, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { CICDIteration, CICDStatus } from '@/types';

interface CICDTimelineProps {
  iterations: CICDIteration[];
  finalStatus: CICDStatus;
}

const statusConfig: Record<CICDStatus, { icon: React.ReactNode; color: string; label: string }> = {
  pending: { icon: <Clock className="h-5 w-5" />, color: 'text-yellow-500', label: 'Pending' },
  running: { icon: <Loader2 className="h-5 w-5 animate-spin" />, color: 'text-blue-500', label: 'Running' },
  passed: { icon: <CheckCircle2 className="h-5 w-5" />, color: 'text-green-500', label: 'Passed' },
  failed: { icon: <XCircle className="h-5 w-5" />, color: 'text-red-500', label: 'Failed' },
  cancelled: { icon: <XCircle className="h-5 w-5" />, color: 'text-gray-500', label: 'Cancelled' },
  timeout: { icon: <Clock className="h-5 w-5" />, color: 'text-orange-500', label: 'Timeout' },
  unknown: { icon: <Clock className="h-5 w-5" />, color: 'text-gray-400', label: 'Unknown' },
};

export function CICDTimeline({ iterations, finalStatus }: CICDTimelineProps) {
  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>CI/CD Timeline</span>
          <Badge 
            variant={finalStatus === 'passed' ? 'default' : 'destructive'}
            className={finalStatus === 'passed' ? 'bg-green-500' : ''}
          >
            {finalStatus.toUpperCase()}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {iterations.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No CI/CD iterations recorded
          </div>
        ) : (
          <div className="space-y-4">
            {iterations.map((iteration, index) => {
              const config = statusConfig[iteration.status];
              
              return (
                <div 
                  key={index}
                  className="flex items-start gap-4 p-4 rounded-lg border bg-card"
                >
                  {/* Status Icon */}
                  <div className={`mt-1 ${config.color}`}>
                    {config.icon}
                  </div>

                  {/* Iteration Details */}
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        Iteration {iteration.iteration}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {formatTimestamp(iteration.timestamp)}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm">
                      <span className={config.color}>
                        {config.label}
                      </span>
                      
                      {iteration.duration_seconds && (
                        <span className="text-muted-foreground">
                          Duration: {formatDuration(iteration.duration_seconds)}
                        </span>
                      )}
                      
                      {iteration.test_failures !== undefined && (
                        <span className="text-muted-foreground">
                          Test Failures: {iteration.test_failures}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Summary */}
            <div className="mt-4 p-4 rounded-lg bg-muted">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{iterations.length}</div>
                  <div className="text-xs text-muted-foreground">Total Iterations</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {iterations.filter(i => i.status === 'passed').length}
                  </div>
                  <div className="text-xs text-muted-foreground">Passed</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {iterations.filter(i => i.status === 'failed').length}
                  </div>
                  <div className="text-xs text-muted-foreground">Failed</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
