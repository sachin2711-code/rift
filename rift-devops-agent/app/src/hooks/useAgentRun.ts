// import { useState, useCallback } from 'react';
// import type { AgentRunResponse, RunData } from '@/types';

// const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// export function useAgentRun() {
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   const startRun = useCallback(async (
//     repository_url: string,
//     team_name: string,
//     team_leader_name: string,
//     max_iterations: number = 5
//   ): Promise<AgentRunResponse> => {
//     setIsLoading(true);
//     setError(null);

//     try {
//       const response = await fetch(`${API_URL}/api/v1/run`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           repository_url,
//           team_name,
//           team_leader_name,
//           max_iterations,
//         }),
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Failed to start run');
//       }

//       const data: AgentRunResponse = await response.json();
//       return data;
//     } catch (err) {
//       const message = err instanceof Error ? err.message : 'Unknown error';
//       setError(message);
//       throw err;
//     } finally {
//       setIsLoading(false);
//     }
//   }, []);

//   const getRunStatus = useCallback(async (runId: string): Promise<RunData> => {
//     const response = await fetch(`${API_URL}/api/v1/status/${runId}`);
    
//     if (!response.ok) {
//       throw new Error('Failed to get run status');
//     }

//     return response.json();
//   }, []);

//   const getRunResults = useCallback(async (runId: string): Promise<RunData> => {
//     const response = await fetch(`${API_URL}/api/v1/results/${runId}`);
    
//     if (!response.ok) {
//       throw new Error('Failed to get run results');
//     }

//     return response.json();
//   }, []);

//   const listRuns = useCallback(async (limit: number = 10, offset: number = 0) => {
//     const response = await fetch(
//       `${API_URL}/api/v1/runs?limit=${limit}&offset=${offset}`
//     );
    
//     if (!response.ok) {
//       throw new Error('Failed to list runs');
//     }

//     return response.json();
//   }, []);

//   const downloadReport = useCallback(async (runId: string): Promise<Blob> => {
//     const response = await fetch(`${API_URL}/api/v1/runs/${runId}/report`);
    
//     if (!response.ok) {
//       throw new Error('Failed to download report');
//     }

//     return response.blob();
//   }, []);

//   return {
//     startRun,
//     getRunStatus,
//     getRunResults,
//     listRuns,
//     downloadReport,
//     isLoading,
//     error,
//   };
// }
import { useState, useCallback } from 'react';
import type { AgentRunResponse, RunData } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useAgentRun() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── ONLY CHANGE: added githubToken as last param ──────────────────────────
  const startRun = useCallback(async (
    repository_url: string,
    team_name: string,
    team_leader_name: string,
    max_iterations: number = 5,
    githubToken: string | null = null   // ← NEW
  ): Promise<AgentRunResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository_url,
          team_name,
          team_leader_name,
          max_iterations,
          github_token: githubToken,    // ← NEW: forwarded to backend
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start run');
      }

      const data: AgentRunResponse = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ── Everything below is UNCHANGED from your original ─────────────────────

  const getRunStatus = useCallback(async (runId: string): Promise<RunData> => {
    const response = await fetch(`${API_URL}/api/v1/status/${runId}`);
    if (!response.ok) throw new Error('Failed to get run status');
    return response.json();
  }, []);

  const getRunResults = useCallback(async (runId: string): Promise<RunData> => {
    const response = await fetch(`${API_URL}/api/v1/results/${runId}`);
    if (!response.ok) throw new Error('Failed to get run results');
    return response.json();
  }, []);

  const listRuns = useCallback(async (limit: number = 10, offset: number = 0) => {
    const response = await fetch(`${API_URL}/api/v1/runs?limit=${limit}&offset=${offset}`);
    if (!response.ok) throw new Error('Failed to list runs');
    return response.json();
  }, []);

  const downloadReport = useCallback(async (runId: string): Promise<Blob> => {
    const response = await fetch(`${API_URL}/api/v1/runs/${runId}/report`);
    if (!response.ok) throw new Error('Failed to download report');
    return response.blob();
  }, []);

  return {
    startRun,
    getRunStatus,
    getRunResults,
    listRuns,
    downloadReport,
    isLoading,
    error,
  };
}