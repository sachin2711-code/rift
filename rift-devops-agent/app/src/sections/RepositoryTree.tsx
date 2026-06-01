import { useState } from 'react';
import { 
  Folder, 
  FolderOpen, 
  FileCode, 
  AlertCircle, 
  CheckCircle2,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { RepositoryFile, Fix } from '@/types';

interface RepositoryTreeProps {
  tree?: RepositoryFile;
  fixes: Fix[];
}

interface TreeNodeProps {
  node: RepositoryFile;
  level: number;
  fixes: Fix[];
}

function TreeNode({ node, level, fixes }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level < 2);

  const getFileFixes = (path: string) => {
    return fixes.filter(f => f.file_path === path);
  };

  const fileFixes = node.type === 'file' ? getFileFixes(node.path) : [];
  const hasErrors = fileFixes.length > 0;
  const isFixed = fileFixes.every(f => f.status === 'verified');

  const getFileIcon = () => {
    if (node.type === 'directory') {
      return isExpanded ? (
        <FolderOpen className="h-4 w-4 text-blue-500" />
      ) : (
        <Folder className="h-4 w-4 text-blue-500" />
      );
    }

    if (hasErrors) {
      if (isFixed) {
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      }
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }

    return <FileCode className="h-4 w-4 text-gray-400" />;
  };

  const getFileClassName = () => {
    if (node.type === 'file') {
      if (hasErrors) {
        return isFixed ? 'bg-green-950/30' : 'bg-red-950/30';
      }
    }
    return '';
  };

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-muted ${getFileClassName()}`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => node.type === 'directory' && setIsExpanded(!isExpanded)}
      >
        {node.type === 'directory' && (
          <span className="text-muted-foreground">
            {isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </span>
        )}
        
        {getFileIcon()}
        
        <span className={`text-sm ${hasErrors ? 'font-medium' : ''}`}>
          {node.name}
        </span>

        {hasErrors && (
          <Badge 
            variant={isFixed ? 'default' : 'destructive'}
            className="text-xs"
          >
            {fileFixes.length} {isFixed ? 'fixed' : 'errors'}
          </Badge>
        )}
      </div>

      {node.type === 'directory' && isExpanded && node.children && (
        <div>
          {node.children.map((child, index) => (
            <TreeNode
              key={index}
              node={child}
              level={level + 1}
              fixes={fixes}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function RepositoryTree({ tree, fixes }: RepositoryTreeProps) {
  if (!tree) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Repository Structure</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No repository data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalErrors = fixes.length;
  const fixedErrors = fixes.filter(f => f.status === 'verified').length;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Repository Structure</span>
          <div className="flex items-center gap-2">
            <Badge variant="destructive">{totalErrors - fixedErrors} errors</Badge>
            <Badge className="bg-green-500">{fixedErrors} fixed</Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="border rounded-lg overflow-hidden">
          <TreeNode node={tree} level={0} fixes={fixes} />
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 mt-4 text-sm">
          <div className="flex items-center gap-1">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <span>Has errors</span>
          </div>
          <div className="flex items-center gap-1">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <span>Fixed</span>
          </div>
          <div className="flex items-center gap-1">
            <FileCode className="h-4 w-4 text-gray-400" />
            <span>No issues</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
