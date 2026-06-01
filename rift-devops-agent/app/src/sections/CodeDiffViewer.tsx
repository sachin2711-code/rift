import { X, FileCode } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { Fix } from '@/types';
import { useRunContext } from '@/App';

interface CodeDiffViewerProps {
  fix: Fix;
}

export function CodeDiffViewer({ fix }: CodeDiffViewerProps) {
  const { setSelectedFix } = useRunContext();

  const renderDiff = () => {
    if (!fix.before_code && !fix.after_code) {
      return (
        <div className="text-center py-8 text-muted-foreground">
          No code diff available
        </div>
      );
    }

    const beforeLines = (fix.before_code || '').split('\n');
    const afterLines = (fix.after_code || '').split('\n');

    return (
      <div className="grid grid-cols-2 gap-4">
        {/* Before */}
        <div className="space-y-2">
          <div className="text-sm font-medium text-red-500">Before</div>
          <div className="bg-red-950/30 border border-red-900 rounded-lg overflow-hidden">
            <pre className="p-4 text-sm font-mono overflow-x-auto">
              {beforeLines.map((line, i) => (
                <div key={i} className="text-red-400">
                  <span className="text-red-600 select-none mr-2">-</span>
                  {line || ' '}
                </div>
              ))}
            </pre>
          </div>
        </div>

        {/* After */}
        <div className="space-y-2">
          <div className="text-sm font-medium text-green-500">After</div>
          <div className="bg-green-950/30 border border-green-900 rounded-lg overflow-hidden">
            <pre className="p-4 text-sm font-mono overflow-x-auto">
              {afterLines.map((line, i) => (
                <div key={i} className="text-green-400">
                  <span className="text-green-600 select-none mr-2">+</span>
                  {line || ' '}
                </div>
              ))}
            </pre>
          </div>
        </div>
      </div>
    );
  };

  const bugTypeColors: Record<string, string> = {
    LINTING: 'bg-blue-500',
    SYNTAX: 'bg-red-500',
    LOGIC: 'bg-purple-500',
    TYPE_ERROR: 'bg-orange-500',
    IMPORT: 'bg-cyan-500',
    INDENTATION: 'bg-yellow-500',
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <FileCode className="h-5 w-5" />
          Code Diff
        </CardTitle>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSelectedFix(null)}
        >
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Fix Info */}
        <div className="flex items-center gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">File:</span>{' '}
            <code className="bg-muted px-2 py-1 rounded">{fix.file_path}</code>
          </div>
          <div>
            <span className="text-muted-foreground">Line:</span>{' '}
            <span className="font-medium">{fix.line_number}</span>
          </div>
          <Badge className={`${bugTypeColors[fix.bug_type] || 'bg-gray-500'} text-white`}>
            {fix.bug_type}
          </Badge>
        </div>

        {/* Description */}
        <div className="text-sm">
          <span className="text-muted-foreground">Description:</span>{' '}
          {fix.description}
        </div>

        {/* Diff */}
        {renderDiff()}

        {/* Commit Message */}
        <div className="text-sm bg-muted p-3 rounded-lg">
          <span className="text-muted-foreground">Commit:</span>{' '}
          <code className="text-xs">{fix.commit_message}</code>
        </div>
      </CardContent>
    </Card>
  );
}
