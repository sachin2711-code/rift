// export type BugType = 
//   | 'LINTING' 
//   | 'SYNTAX' 
//   | 'LOGIC' 
//   | 'TYPE_ERROR' 
//   | 'IMPORT' 
//   | 'INDENTATION' 
//   | 'UNUSED'
//   | 'SECURITY'
//   | 'PERFORMANCE'
//   | 'TEST_FAILURE';

// export type FixStatus = 'pending' | 'applied' | 'verified' | 'failed' | 'rolled_back';

// export type CICDStatus = 'pending' | 'running' | 'passed' | 'failed' | 'cancelled' | 'timeout' | 'unknown';

// export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// export type AgentStage = 
//   | 'initializing'
//   | 'cloning_repository'
//   | 'analyzing'
//   | 'analysis_complete'
//   | 'learning'
//   | 'learning_complete'
//   | 'fixing'
//   | 'fixing_complete'
//   | 'committing'
//   | 'committing_complete'
//   | 'watching_ci'
//   | 'ci_watching_complete'
//   | 'finalizing'
//   | 'completed'
//   | 'error';

// export interface Fix {
//   id: string;
//   file_path: string;
//   bug_type: BugType;
//   line_number: number;
//   line_end?: number;
//   commit_message: string;
//   status: FixStatus;
//   description: string;
//   before_code?: string;
//   after_code?: string;
//   error_message?: string;
//   timestamp: string;
// }

// export interface CICDIteration {
//   iteration: number;
//   status: CICDStatus;
//   timestamp: string;
//   duration_seconds?: number;
//   test_failures?: number;
//   logs_url?: string;
// }

// export interface ScoreBreakdown {
//   base_score: number;
//   speed_bonus: number;
//   efficiency_penalty: number;
//   success_bonus: number;
//   total_score: number;
//   time_taken_seconds: number;
// }

// export interface RepositoryFile {
//   name: string;
//   path: string;
//   type: 'file' | 'directory';
//   size?: number;
//   has_errors?: boolean;
//   error_count?: number;
//   fixed?: boolean;
//   children?: RepositoryFile[];
// }

// export interface RunData {
//   run_id: string;
//   repository_url: string;
//   team_name: string;
//   team_leader_name: string;
//   branch_name: string;
//   status: RunStatus;
  
//   // Timestamps
//   started_at?: string;
//   completed_at?: string;
//   duration_seconds?: number;
  
//   // Results
//   total_failures: number;
//   total_fixes: number;
//   cicd_iterations: CICDIteration[];
//   final_cicd_status: CICDStatus;
  
//   // Details
//   fixes: Fix[];
//   score: ScoreBreakdown;
//   file_tree?: RepositoryFile;
  
//   // Links
//   pull_request_url?: string;
//   commit_sha?: string;
  
//   // Error info
//   error_message?: string;
  
//   // UI state
//   stage?: AgentStage;
//   progress?: number;
//   message?: string;
// }

// export interface AgentRunRequest {
//   repository_url: string;
//   team_name: string;
//   team_leader_name: string;
//   max_iterations?: number;
// }

// export interface AgentRunResponse {
//   run_id: string;
//   status: string;
//   message: string;
//   branch_name: string;
//   estimated_time: number;
// }

// export interface BugPattern {
//   id: string;
//   bug_type: BugType;
//   pattern: string;
//   fix_template: string;
//   occurrence_count: number;
//   success_count: number;
//   success_rate: number;
//   file_extensions: string[];
//   example_files: string[];
//   created_at: string;
//   last_seen_at: string;
// }

// export interface HeatmapData {
//   path: string;
//   error_count: number;
//   fix_count: number;
//   file_count: number;
//   intensity: number;
// }

// export interface ComparisonResult {
//   run1: RunSummary;
//   run2: RunSummary;
//   differences: {
//     fixes_difference: number;
//     time_difference: number;
//     score_difference: number;
//   };
// }

// export interface RunSummary {
//   run_id: string;
//   repository_url: string;
//   team_name: string;
//   status: RunStatus;
//   created_at: string;
//   completed_at?: string;
//   total_fixes: number;
//   final_cicd_status?: CICDStatus;
//   total_score?: number;
// }

// export interface WebSocketMessage {
//   type: string;
//   run_id: string;
//   timestamp: string;
//   data: Record<string, any>;
// }
export type BugType = 
  | 'LINTING' 
  | 'SYNTAX' 
  | 'LOGIC' 
  | 'TYPE_ERROR' 
  | 'IMPORT' 
  | 'INDENTATION' 
  | 'UNUSED'
  | 'SECURITY'
  | 'PERFORMANCE'
  | 'TEST_FAILURE';

export type FixStatus = 'pending' | 'applied' | 'verified' | 'failed' | 'rolled_back';

export type CICDStatus = 'pending' | 'running' | 'passed' | 'failed' | 'cancelled' | 'timeout' | 'unknown';

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export type AgentStage = 
  | 'initializing'
  | 'cloning_repository'
  | 'analyzing'
  | 'analysis_complete'
  | 'learning'
  | 'learning_complete'
  | 'fixing'
  | 'fixing_complete'
  | 'committing'
  | 'committing_complete'
  | 'results_ready'         // ✅ emitted after committer — frontend unlocks here
  | 'watching_ci'
  | 'ci_watching_complete'
  | 'finalizing'
  | 'completed'
  | 'error';

export interface Fix {
  id: string;
  file_path: string;
  bug_type: BugType;
  line_number: number;
  line_end?: number;
  commit_message: string;
  status: FixStatus;
  description: string;
  before_code?: string;
  after_code?: string;
  error_message?: string;
  timestamp: string;
}

export interface CICDIteration {
  iteration: number;
  status: CICDStatus;
  timestamp: string;
  duration_seconds?: number;
  test_failures?: number;
  logs_url?: string;
}

export interface ScoreBreakdown {
  base_score: number;
  speed_bonus: number;
  efficiency_penalty: number;
  success_bonus: number;
  total_score: number;
  time_taken_seconds: number;
}

export interface RepositoryFile {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  has_errors?: boolean;
  error_count?: number;
  fixed?: boolean;
  children?: RepositoryFile[];
}

export interface RunData {
  run_id: string;
  repository_url: string;
  team_name: string;
  team_leader_name: string;
  branch_name: string;
  status: RunStatus;

  // Timestamps
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;

  // Results
  total_failures: number;
  total_fixes: number;
  total_commits?: number;
  cicd_iterations: CICDIteration[];
  final_cicd_status: CICDStatus;
  current_iteration?: number;

  // Details
  fixes: Fix[];
  applied_fixes?: Fix[];    // ✅ fixes successfully applied by the agent
  failed_fixes?: Fix[];     // ✅ fixes the agent attempted but failed
  score: ScoreBreakdown;
  file_tree?: RepositoryFile;

  // Links
  pull_request_url?: string;
  commit_sha?: string;
  repo_name?: string;

  // Error info
  error_message?: string;
  success?: boolean;

  // UI state (populated from socket events)
  stage?: AgentStage;
  progress?: number;
  message?: string;
}

export interface AgentRunRequest {
  repository_url: string;
  team_name: string;
  team_leader_name: string;
  max_iterations?: number;
}

export interface AgentRunResponse {
  run_id: string;
  status: string;
  message: string;
  branch_name: string;
  estimated_time: number;
}

export interface BugPattern {
  id: string;
  bug_type: BugType;
  pattern: string;
  fix_template: string;
  occurrence_count: number;
  success_count: number;
  success_rate: number;
  file_extensions: string[];
  example_files: string[];
  created_at: string;
  last_seen_at: string;
}

export interface HeatmapData {
  path: string;
  error_count: number;
  fix_count: number;
  file_count: number;
  intensity: number;
}

export interface ComparisonResult {
  run1: RunSummary;
  run2: RunSummary;
  differences: {
    fixes_difference: number;
    time_difference: number;
    score_difference: number;
  };
}

export interface RunSummary {
  run_id: string;
  repository_url: string;
  team_name: string;
  status: RunStatus;
  created_at: string;
  completed_at?: string;
  total_fixes: number;
  final_cicd_status?: CICDStatus;
  total_score?: number;
}

export interface WebSocketMessage {
  type: string;
  run_id: string;
  timestamp: string;
  data: Record<string, any>;
}