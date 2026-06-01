import { useEffect, useState } from 'react';
import { History, GitCompare, Download, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import type { RunSummary, ComparisonResult } from '@/types';
import { useAgentRun } from '@/hooks/useAgentRun';
import { toast } from 'sonner';

export function HistoricalRuns() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRuns, setSelectedRuns] = useState<string[]>([]);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const { listRuns, downloadReport } = useAgentRun();

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const data = await listRuns(20, 0);
      setRuns(data.runs || []);
    } catch (error) {
      toast.error('Failed to load runs');
    }
  };

  const handleSelectRun = (runId: string) => {
    setSelectedRuns(prev => {
      if (prev.includes(runId)) {
        return prev.filter(id => id !== runId);
      }
      if (prev.length >= 2) {
        return [prev[1], runId];
      }
      return [...prev, runId];
    });
  };

  const handleCompare = async () => {
    if (selectedRuns.length !== 2) {
      toast.error('Please select exactly 2 runs to compare');
      return;
    }

    try {
      const response = await fetch(
        `/api/v1/runs/${selectedRuns[0]}/compare/${selectedRuns[1]}`
      );
      const data = await response.json();
      setComparison(data);
    } catch (error) {
      toast.error('Failed to compare runs');
    }
  };

  const handleDownloadReport = async (runId: string) => {
    try {
      const blob = await downloadReport(runId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rift_report_${runId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'passed':
        return <Badge className="bg-green-500">PASSED</Badge>;
      case 'failed':
        return <Badge variant="destructive">FAILED</Badge>;
      default:
        return <Badge variant="secondary">{status.toUpperCase()}</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Historical Runs
          </div>
          {selectedRuns.length === 2 && (
            <Button onClick={handleCompare} size="sm">
              <GitCompare className="h-4 w-4 mr-2" />
              Compare Selected
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Comparison Result */}
        {comparison && (
          <div className="p-4 bg-muted rounded-lg space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Comparison Result</h4>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setComparison(null)}
              >
                Clear
              </Button>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-sm text-muted-foreground">Fixes Difference</div>
                <div className={`text-xl font-bold ${
                  comparison.differences.fixes_difference >= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {comparison.differences.fixes_difference > 0 ? '+' : ''}
                  {comparison.differences.fixes_difference}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Time Difference</div>
                <div className={`text-xl font-bold ${
                  comparison.differences.time_difference <= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {comparison.differences.time_difference > 0 ? '+' : ''}
                  {comparison.differences.time_difference.toFixed(1)}s
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Score Difference</div>
                <div className={`text-xl font-bold ${
                  comparison.differences.score_difference >= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {comparison.differences.score_difference > 0 ? '+' : ''}
                  {comparison.differences.score_difference}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Runs Table */}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10"></TableHead>
                <TableHead>Repository</TableHead>
                <TableHead>Team</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Fixes</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.run_id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedRuns.includes(run.run_id)}
                      onCheckedChange={() => handleSelectRun(run.run_id)}
                    />
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {run.repository_url}
                  </TableCell>
                  <TableCell>{run.team_name}</TableCell>
                  <TableCell>
                    {getStatusBadge(run.final_cicd_status || 'unknown')}
                  </TableCell>
                  <TableCell>{run.total_fixes}</TableCell>
                  <TableCell>{run.total_score || 'N/A'}</TableCell>
                  <TableCell>{formatDate(run.created_at)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDownloadReport(run.run_id)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" asChild>
                        <a href={`/run/${run.run_id}`} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {runs.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No historical runs found
          </div>
        )}
      </CardContent>
    </Card>
  );
}
