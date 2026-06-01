import { useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface LiveArchitectureProps {
  stage: string;
  progress: number;
}

const agentNodes = [
  { id: 'analyzer', label: 'Analyzer', x: 100, y: 100 },
  { id: 'learner', label: 'Learner', x: 300, y: 100 },
  { id: 'fixer', label: 'Fixer', x: 500, y: 100 },
  { id: 'committer', label: 'Committer', x: 700, y: 100 },
  { id: 'ci-watcher', label: 'CI Watcher', x: 900, y: 100 },
];

const stageToAgent: Record<string, string> = {
  cloning_repository: 'analyzer',
  analyzing: 'analyzer',
  analysis_complete: 'analyzer',
  learning: 'learner',
  learning_complete: 'learner',
  fixing: 'fixer',
  fixing_complete: 'fixer',
  committing: 'committer',
  committing_complete: 'committer',
  watching_ci: 'ci-watcher',
  ci_watching_complete: 'ci-watcher',
  finalizing: 'ci-watcher',
  completed: 'ci-watcher',
};

export function LiveArchitecture({ stage, progress }: LiveArchitectureProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [activeAgent , setActiveAgent] = useState<string | null>(null);

  // Initialize nodes
  useEffect(() => {
    const initialNodes: Node[] = agentNodes.map((agent) => ({
      id: agent.id,
      position: { x: agent.x, y: agent.y },
      data: { label: agent.label },
      style: {
        background: '#3b82f6',
        color: 'white',
        border: '2px solid #1d4ed8',
        borderRadius: '8px',
        padding: '10px 20px',
        fontWeight: 'bold',
        width: 120,
      },
    }));
    setNodes(initialNodes);
  }, []);

  // Initialize edges
  useEffect(() => {
    const initialEdges: Edge[] = [
      {
        id: 'e1',
        source: 'analyzer',
        target: 'learner',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      },
      {
        id: 'e2',
        source: 'learner',
        target: 'fixer',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      },
      {
        id: 'e3',
        source: 'fixer',
        target: 'committer',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      },
      {
        id: 'e4',
        source: 'committer',
        target: 'ci-watcher',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      },
      {
        id: 'e5',
        source: 'ci-watcher',
        target: 'fixer',
        animated: false,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#ef4444', strokeWidth: 2, strokeDasharray: '5,5' },
        label: 'Retry',
      },
    ];
    setEdges(initialEdges);
  }, []);

  // Update active agent based on stage
  useEffect(() => {
    const currentAgent = stageToAgent[stage];
    setActiveAgent(currentAgent);

    // Update node styles based on active agent
    setNodes((prevNodes) =>
      prevNodes.map((node) => ({
        ...node,
        style: {
          ...node.style,
          background: node.id === currentAgent ? '#22c55e' : '#3b82f6',
          border: node.id === currentAgent ? '3px solid #16a34a' : '2px solid #1d4ed8',
          boxShadow: node.id === currentAgent ? '0 0 20px rgba(34, 197, 94, 0.5)' : 'none',
        },
      }))
    );

    // Update edge animations
    setEdges((prevEdges) =>
      prevEdges.map((edge) => ({
        ...edge,
        animated:
          edge.source === currentAgent ||
          (currentAgent === 'ci-watcher' && edge.source === 'ci-watcher' && edge.target === 'fixer'),
        style: {
          ...edge.style,
          stroke: edge.source === currentAgent ? '#22c55e' : edge.style?.stroke,
        },
      }))
    );
  }, [stage, setNodes, setEdges]);

  const getStageDisplayName = (stage: string) => {
    return stage
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Live Architecture</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Current Stage:</span>
            <span className="font-medium">{getStageDisplayName(stage)}</span>
          </div>
          <Progress value={progress} className="h-2" />
          <div className="text-right text-sm text-muted-foreground">
            {progress}%
          </div>
        </div>

        {/* Agent Flow Graph */}
        <div className="h-[300px] border rounded-lg overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-right"
          >
            <Background color="#94a3b8" gap={16} />
            <Controls />
          </ReactFlow>
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-500" />
            <span>Idle</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500" />
            <span>Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-blue-500 border-dashed rounded" />
            <span>Retry Loop</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
