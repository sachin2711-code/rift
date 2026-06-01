import { 
  GitBranch, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle,
  ExternalLink,
  Download
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import type { RunData } from '@/types';
import { useAgentRun } from '@/hooks/useAgentRun';

interface RunSummaryCardProps {
  runData: RunData;
}

export function RunSummaryCard({ runData }: RunSummaryCardProps) {
  const { downloadReport } = useAgentRun();

  const handleDownloadReport = async () => {
    try {
      const blob = await downloadReport(runData.run_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rift_report_${runData.run_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'passed':
        return (
          <Badge className="bg-green-500 hover:bg-green-600">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            PASSED
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="destructive">
            <XCircle className="h-3 w-3 mr-1" />
            FAILED
          </Badge>
        );
      default:
        return (
          <Badge variant="secondary">
            <AlertTriangle className="h-3 w-3 mr-1" />
            {status.toUpperCase()}
          </Badge>
        );
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Run Summary</span>
          {getStatusBadge(runData.final_cicd_status)}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Repository Info */}
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground">Repository</div>
          <div className="font-medium truncate">{runData.repository_url}</div>
        </div>

        <Separator />

        {/* Team Info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Team</div>
            <div className="font-medium">{runData.team_name}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Leader</div>
            <div className="font-medium">{runData.team_leader_name}</div>
          </div>
        </div>

        <Separator />

        {/* Branch Info */}
        <div className="flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-muted-foreground" />
          <code className="text-sm bg-muted px-2 py-1 rounded">
            {runData.branch_name}
          </code>
        </div>

        <Separator />

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{runData.total_failures}</div>
            <div className="text-xs text-muted-foreground">Failures</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{runData.total_fixes}</div>
            <div className="text-xs text-muted-foreground">Fixes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{runData.cicd_iterations.length}</div>
            <div className="text-xs text-muted-foreground">Iterations</div>
          </div>
        </div>

        <Separator />

        {/* Duration */}
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Duration:</span>
          <span className="font-medium">{formatDuration(runData.duration_seconds)}</span>
        </div>

        {/* Links */}
        {runData.pull_request_url && (
          <div className="flex items-center gap-2">
            <ExternalLink className="h-4 w-4 text-muted-foreground" />
            <a 
              href={runData.pull_request_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              View Pull Request
            </a>
          </div>
        )}

        {/* Download Report */}
        <Button 
          variant="outline" 
          className="w-full"
          onClick={handleDownloadReport}
        >
          <Download className="h-4 w-4 mr-2" />
          Download PDF Report
        </Button>
      </CardContent>
    </Card>
  );
}
