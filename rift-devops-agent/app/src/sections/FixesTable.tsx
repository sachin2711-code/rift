import { CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { Fix, FixStatus, BugType } from '@/types';
import { useRunContext } from '@/App';

interface FixesTableProps {
  fixes: Fix[];
}

const bugTypeColors: Record<BugType, string> = {
  LINTING: 'bg-blue-500',
  SYNTAX: 'bg-red-500',
  LOGIC: 'bg-purple-500',
  TYPE_ERROR: 'bg-orange-500',
  IMPORT: 'bg-cyan-500',
  INDENTATION: 'bg-yellow-500',
  UNUSED: 'bg-gray-500',
  SECURITY: 'bg-red-600',
  PERFORMANCE: 'bg-green-500',
  TEST_FAILURE: 'bg-pink-500',
};

const statusIcons: Record<FixStatus, React.ReactNode> = {
  pending: <Clock className="h-4 w-4 text-yellow-500" />,
  applied: <CheckCircle2 className="h-4 w-4 text-blue-500" />,
  verified: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  failed: <XCircle className="h-4 w-4 text-red-500" />,
  rolled_back: <AlertCircle className="h-4 w-4 text-orange-500" />,
};

export function FixesTable({ fixes }: FixesTableProps) {
  const { setSelectedFix } = useRunContext();

  if (fixes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Fixes Applied</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No fixes applied
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Fixes Applied ({fixes.length})</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>File</TableHead>
                <TableHead>Bug Type</TableHead>
                <TableHead>Line</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {fixes.map((fix) => (
                <TableRow key={fix.id}>
                  <TableCell className="font-mono text-sm max-w-[200px] truncate">
                    {fix.file_path}
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant="secondary"
                      className={`${bugTypeColors[fix.bug_type]} text-white`}
                    >
                      {fix.bug_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    {fix.line_number}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {statusIcons[fix.status]}
                      <span className="capitalize">{fix.status}</span>
                    </div>
                  </TableCell>
                  <TableCell className="max-w-[250px] truncate">
                    {fix.description}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedFix(fix)}
                    >
                      View Diff
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
