// // import { useState, useEffect, createContext, useContext } from 'react';
// // import { ThemeProvider } from '@/components/theme-provider';
// // import { Toaster } from '@/components/ui/sonner';
// // import { toast } from 'sonner';
// // import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// // // Sections
// // import { InputSection } from '@/sections/InputSection';
// // import { RunSummaryCard } from '@/sections/RunSummaryCard';
// // import { ScoreBreakdownPanel } from '@/sections/ScoreBreakdownPanel';
// // import { FixesTable } from '@/sections/FixesTable';
// // import { CICDTimeline } from '@/sections/CICDTimeline';
// // import { LiveArchitecture } from '@/sections/LiveArchitecture';
// // import { CodeDiffViewer } from '@/sections/CodeDiffViewer';
// // import { RepositoryTree } from '@/sections/RepositoryTree';
// // import { BugHeatmap } from '@/sections/BugHeatmap';
// // import { HistoricalRuns } from '@/sections/HistoricalRuns';
// // import { Header } from '@/sections/Header';

// // // Hooks
// // import { useSocket } from '@/hooks/useSocket';
// // import { useAgentRun } from '@/hooks/useAgentRun';

// // // Types
// // import type { RunData, Fix } from '@/types';

// // // Context for run data
// // interface RunContextType {
// //   runData: RunData | null;
// //   isRunning: boolean;
// //   selectedFix: Fix | null;
// //   setSelectedFix: (fix: Fix | null) => void;
// // }

// // const RunContext = createContext<RunContextType>({
// //   runData: null,
// //   isRunning: false,
// //   selectedFix: null,
// //   setSelectedFix: () => {},
// // });

// // export const useRunContext = () => useContext(RunContext);

// // function App() {
// //   const [runData, setRunData] = useState<RunData | null>(null);
// //   const [isRunning, setIsRunning] = useState(false);
// //   const [selectedFix, setSelectedFix] = useState<Fix | null>(null);
// //   const [activeTab, setActiveTab] = useState('overview');

// //   const { socket, isConnected } = useSocket();
// //   const { startRun } = useAgentRun();

// //   useEffect(() => {
// //     if (socket) {
// //       socket.on('run_update', (data: any) => {
// //         console.log('Run update:', data);
        
// //         if (data.data) {
// //           setRunData(prev => ({
// //             ...prev,
// //             ...data.data.result,
// //             stage: data.data.stage,
// //             progress: data.data.progress,
// //             message: data.data.message,
// //           }));

// //           // Show toast for important updates
// //           if (data.data.stage === 'completed') {
// //             toast.success('Agent run completed!');
// //             setIsRunning(false);
// //           } else if (data.data.stage === 'error') {
// //             toast.error(`Error: ${data.data.message}`);
// //             setIsRunning(false);
// //           }
// //         }
// //       });

// //       return () => {
// //         socket.off('run_update');
// //       };
// //     }
// //   }, [socket]);

// //   const handleStartRun = async (repoUrl: string, teamName: string, teamLeader: string) => {
// //     setIsRunning(true);
// //     setRunData(null);
// //     setSelectedFix(null);

// //     try {
// //       const result = await startRun(repoUrl, teamName, teamLeader);
      
// //       if (result.run_id && socket) {
// //         socket.emit('subscribe_run', { run_id: result.run_id });
// //       }

// //       toast.success('Agent run started!');
// //     } catch (error) {
// //       toast.error('Failed to start agent run');
// //       setIsRunning(false);
// //     }
// //   };

// //   return (
// //     <ThemeProvider defaultTheme="dark" storageKey="rift-theme">
// //       <RunContext.Provider value={{ runData, isRunning, selectedFix, setSelectedFix }}>
// //         <div className="min-h-screen bg-background">
// //           <Header isConnected={isConnected} />
          
// //           <main className="container mx-auto px-4 py-6 space-y-6">
// //             {/* Input Section */}
// //             <InputSection 
// //               onStartRun={handleStartRun} 
// //               isRunning={isRunning} 
// //             />

// //             {/* Live Architecture Visualization */}
// //             {isRunning && (
// //               <LiveArchitecture 
// //                 stage={runData?.stage || 'initializing'}
// //                 progress={runData?.progress || 0}
// //               />
// //             )}

// //             {/* Results Tabs */}
// //             {runData && !isRunning && (
// //               <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
// //                 <TabsList className="grid w-full grid-cols-6">
// //                   <TabsTrigger value="overview">Overview</TabsTrigger>
// //                   <TabsTrigger value="fixes">Fixes</TabsTrigger>
// //                   <TabsTrigger value="cicd">CI/CD</TabsTrigger>
// //                   <TabsTrigger value="tree">File Tree</TabsTrigger>
// //                   <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
// //                   <TabsTrigger value="history">History</TabsTrigger>
// //                 </TabsList>

// //                 <TabsContent value="overview" className="space-y-6">
// //                   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
// //                     <RunSummaryCard runData={runData} />
// //                     <ScoreBreakdownPanel score={runData.score} />
// //                   </div>
// //                 </TabsContent>

// //                 <TabsContent value="fixes">
// //                   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
// //                     <FixesTable fixes={runData.fixes || []} />
// //                     {selectedFix && <CodeDiffViewer fix={selectedFix} />}
// //                   </div>
// //                 </TabsContent>

// //                 <TabsContent value="cicd">
// //                   <CICDTimeline 
// //                     iterations={runData.cicd_iterations || []} 
// //                     finalStatus={runData.final_cicd_status}
// //                   />
// //                 </TabsContent>

// //                 <TabsContent value="tree">
// //                   <RepositoryTree 
// //                     tree={runData.file_tree} 
// //                     fixes={runData.fixes || []}
// //                   />
// //                 </TabsContent>

// //                 <TabsContent value="heatmap">
// //                   <BugHeatmap fixes={runData.fixes || []} />
// //                 </TabsContent>

// //                 <TabsContent value="history">
// //                   <HistoricalRuns />
// //                 </TabsContent>
// //               </Tabs>
// //             )}
// //           </main>

// //           <Toaster />
// //         </div>
// //       </RunContext.Provider>
// //     </ThemeProvider>
// //   );
// // }

// // export default App;
// import { useState, useEffect, createContext, useContext } from 'react';
// import { ThemeProvider } from '@/components/theme-provider';
// import { Toaster } from '@/components/ui/sonner';
// import { toast } from 'sonner';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// // Sections
// import { InputSection } from '@/sections/InputSection';
// import { RunSummaryCard } from '@/sections/RunSummaryCard';
// import { ScoreBreakdownPanel } from '@/sections/ScoreBreakdownPanel';
// import { FixesTable } from '@/sections/FixesTable';
// import { CICDTimeline } from '@/sections/CICDTimeline';
// import { LiveArchitecture } from '@/sections/LiveArchitecture';
// import { CodeDiffViewer } from '@/sections/CodeDiffViewer';
// import { RepositoryTree } from '@/sections/RepositoryTree';
// import { BugHeatmap } from '@/sections/BugHeatmap';
// import { HistoricalRuns } from '@/sections/HistoricalRuns';
// import { Header } from '@/sections/Header';

// // Hooks
// import { useSocket } from '@/hooks/useSocket';
// import { useAgentRun } from '@/hooks/useAgentRun';

// // Types
// import type { RunData, Fix } from '@/types';

// // Context for run data
// interface RunContextType {
//   runData: RunData | null;
//   isRunning: boolean;
//   isCIWatching: boolean;
//   selectedFix: Fix | null;
//   setSelectedFix: (fix: Fix | null) => void;
// }

// const RunContext = createContext<RunContextType>({
//   runData: null,
//   isRunning: false,
//   isCIWatching: false,
//   selectedFix: null,
//   setSelectedFix: () => {},
// });

// export const useRunContext = () => useContext(RunContext);

// function App() {
//   const [runData, setRunData] = useState<RunData | null>(null);

//   // isRunning = true while agents are working AND results not yet available
//   const [isRunning, setIsRunning] = useState(false);

//   // isCIWatching = true after results shown but CI watcher still running in background
//   const [isCIWatching, setIsCIWatching] = useState(false);

//   const [selectedFix, setSelectedFix] = useState<Fix | null>(null);
//   const [activeTab, setActiveTab] = useState('overview');

//   const { socket, isConnected } = useSocket();
//   const { startRun } = useAgentRun();

//   useEffect(() => {
//     if (socket) {
//       socket.on('run_update', (data: any) => {
//         console.log('Run update:', data);

//         if (data.data) {
//           const { stage, message, progress, result } = data.data;

//           // Always merge latest data into runData
//           setRunData(prev => ({
//             ...prev,
//             ...(result || {}),
//             stage,
//             progress,
//             message,
//           }));

//           switch (stage) {
//             // ✅ KEY STAGE: fixes committed, results ready — unlock the UI now
//             // CI watcher will still run in background and update cicd tab silently
//             case 'results_ready':
//               setIsRunning(false);      // stop the loading screen
//               setIsCIWatching(true);    // flag that ci watcher is still running
//               toast.success('Fixes ready! CI/CD monitoring running in background...');
//               break;

//             // CI watcher finished — update cicd tab silently, no UI disruption
//             case 'ci_watching_complete':
//               setIsCIWatching(false);
//               toast.info(`CI/CD check complete: ${result?.final_cicd_status?.toUpperCase() || 'UNKNOWN'}`);
//               break;

//             // Full pipeline done (after finalize — PR created etc.)
//             case 'completed':
//               setIsRunning(false);
//               setIsCIWatching(false);
//               toast.success('🎉 Agent run fully complete!');
//               break;

//             case 'error':
//               setIsRunning(false);
//               setIsCIWatching(false);
//               toast.error(`Error: ${message}`);
//               break;

//             // Intermediate stages — just show progress, no state change needed
//             default:
//               break;
//           }
//         }
//       });

//       return () => {
//         socket.off('run_update');
//       };
//     }
//   }, [socket]);

//   const handleStartRun = async (repoUrl: string, teamName: string, teamLeader: string) => {
//     setIsRunning(true);
//     setIsCIWatching(false);
//     setRunData(null);
//     setSelectedFix(null);
//     setActiveTab('overview');

//     try {
//       const result = await startRun(repoUrl, teamName, teamLeader);

//       if (result.run_id && socket) {
//         socket.emit('subscribe_run', { run_id: result.run_id });
//       }

//       toast.success('Agent run started!');
//     } catch (error) {
//       toast.error('Failed to start agent run');
//       setIsRunning(false);
//     }
//   };

//   // Show results if we have fixes data, regardless of isRunning
//   // This means results show as soon as results_ready fires
//   const showResults = !!(runData?.fixes || runData?.applied_fixes);

//   return (
//     <ThemeProvider defaultTheme="dark" storageKey="rift-theme">
//       <RunContext.Provider value={{ runData, isRunning, isCIWatching, selectedFix, setSelectedFix }}>
//         <div className="min-h-screen bg-background">
//           <Header isConnected={isConnected} />

//           <main className="container mx-auto px-4 py-6 space-y-6">
//             {/* Input Section */}
//             <InputSection
//               onStartRun={handleStartRun}
//               isRunning={isRunning}
//             />

//             {/* Live Architecture — only show while agents are actively running (before results_ready) */}
//             {isRunning && (
//               <LiveArchitecture
//                 stage={runData?.stage || 'initializing'}
//                 progress={runData?.progress || 0}
//               />
//             )}

//             {/* 
//               Results Tabs — show as soon as fixes are available (results_ready stage).
//               Does NOT wait for CI watcher to finish.
//             */}
//             {showResults && (
//               <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
//                 <TabsList className="grid w-full grid-cols-6">
//                   <TabsTrigger value="overview">Overview</TabsTrigger>
//                   <TabsTrigger value="fixes">
//                     Fixes
//                     {runData?.applied_fixes?.length ? (
//                       <span className="ml-1.5 text-xs bg-primary text-primary-foreground rounded-full px-1.5">
//                         {runData.applied_fixes.length}
//                       </span>
//                     ) : null}
//                   </TabsTrigger>
//                   <TabsTrigger value="cicd">
//                     CI/CD
//                     {/* Show spinner badge while CI watcher is still running */}
//                     {isCIWatching && (
//                       <span className="ml-1.5 text-xs bg-yellow-500 text-black rounded-full px-1.5 animate-pulse">
//                         Live
//                       </span>
//                     )}
//                   </TabsTrigger>
//                   <TabsTrigger value="tree">File Tree</TabsTrigger>
//                   <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
//                   <TabsTrigger value="history">History</TabsTrigger>
//                 </TabsList>

//                 {/* Overview Tab */}
//                 <TabsContent value="overview" className="space-y-6">
//                   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//                     <RunSummaryCard runData={runData} />
//                     <ScoreBreakdownPanel score={runData?.score} />
//                   </div>
//                 </TabsContent>

//                 {/* Fixes Tab */}
//                 <TabsContent value="fixes">
//                   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//                     <FixesTable fixes={runData?.fixes || runData?.applied_fixes || []} />
//                     {selectedFix && <CodeDiffViewer fix={selectedFix} />}
//                   </div>
//                 </TabsContent>

//                 {/* CI/CD Tab — shows spinner while CI watcher is running, populates when done */}
//                 <TabsContent value="cicd">
//                   {isCIWatching && (!runData?.cicd_iterations || runData.cicd_iterations.length === 0) ? (
//                     <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
//                       <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-4" />
//                       <p className="text-sm font-medium">Monitoring CI/CD pipeline...</p>
//                       <p className="text-xs mt-1 opacity-60">This runs in the background. Other tabs are fully available.</p>
//                     </div>
//                   ) : (
//                     <CICDTimeline
//                       iterations={runData?.cicd_iterations || []}
//                       finalStatus={runData?.final_cicd_status}
                      
//                     />
//                   )}
//                 </TabsContent>

//                 {/* File Tree Tab */}
//                 <TabsContent value="tree">
//                   <RepositoryTree
//                     tree={runData?.file_tree}
//                     fixes={runData?.fixes || runData?.applied_fixes || []}
//                   />
//                 </TabsContent>

//                 {/* Heatmap Tab */}
//                 <TabsContent value="heatmap">
//                   <BugHeatmap fixes={runData?.fixes || runData?.applied_fixes || []} />
//                 </TabsContent>

//                 {/* History Tab */}
//                 <TabsContent value="history">
//                   <HistoricalRuns />
//                 </TabsContent>
//               </Tabs>
//             )}
//           </main>

//           <Toaster />
//         </div>
//       </RunContext.Provider>
//     </ThemeProvider>
//   );
// }

// export default App;
import { useState, useEffect, createContext, useContext } from 'react';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Sections
import { InputSection } from '@/sections/InputSection';
import { RunSummaryCard } from '@/sections/RunSummaryCard';
import { ScoreBreakdownPanel } from '@/sections/ScoreBreakdownPanel';
import { FixesTable } from '@/sections/FixesTable';
import { CICDTimeline } from '@/sections/CICDTimeline';
import { LiveArchitecture } from '@/sections/LiveArchitecture';
import { CodeDiffViewer } from '@/sections/CodeDiffViewer';
import { RepositoryTree } from '@/sections/RepositoryTree';
import { BugHeatmap } from '@/sections/BugHeatmap';
import { HistoricalRuns } from '@/sections/HistoricalRuns';
import { Header } from '@/sections/Header';

// Hooks
import { useSocket } from '@/hooks/useSocket';
import { useAgentRun } from '@/hooks/useAgentRun';

// Types
import type { RunData, Fix } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ─── Auth types ───────────────────────────────────────────────────────────────
interface AuthUser {
  token: string;
  username: string;
  avatar: string;
}

// ─── Run context ──────────────────────────────────────────────────────────────
interface RunContextType {
  runData: RunData | null;
  isRunning: boolean;
  isCIWatching: boolean;
  selectedFix: Fix | null;
  setSelectedFix: (fix: Fix | null) => void;
  // Auth
  user: AuthUser | null;
  login: () => void;
  logout: () => void;
}

const RunContext = createContext<RunContextType>({
  runData: null,
  isRunning: false,
  isCIWatching: false,
  selectedFix: null,
  setSelectedFix: () => {},
  user: null,
  login: () => {},
  logout: () => {},
});

export const useRunContext = () => useContext(RunContext);

// ─── GitHub Login Button component ───────────────────────────────────────────
function GitHubLoginButton({ user, onLogin, onLogout }: {
  user: AuthUser | null;
  onLogin: () => void;
  onLogout: () => void;
}) {
  if (user) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {user.avatar && (
          <img
            src={user.avatar}
            alt={user.username}
            style={{ width: 30, height: 30, borderRadius: '50%', border: '2px solid #00ff88' }}
          />
        )}
        <span style={{ fontSize: 13, fontFamily: 'monospace', color: '#00ff88' }}>
          @{user.username}
        </span>
        <button
          onClick={onLogout}
          className="text-xs text-muted-foreground hover:text-destructive transition-colors"
        >
          logout
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={onLogin}
      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#161b22] border border-[#30363d] text-white text-sm font-semibold hover:border-green-400 transition-all"
    >
      <svg height="18" width="18" viewBox="0 0 16 16" fill="currentColor">
        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
                 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
                 -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
                 .07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
                 -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0
                 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82
                 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01
                 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
      </svg>
      Login with GitHub
    </button>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
function App() {
  const [runData, setRunData]       = useState<RunData | null>(null);
  const [isRunning, setIsRunning]   = useState(false);
  const [isCIWatching, setIsCIWatching] = useState(false);
  const [selectedFix, setSelectedFix]   = useState<Fix | null>(null);
  const [activeTab, setActiveTab]       = useState('overview');

  // ── Auth state ──────────────────────────────────────────────────────────────
  const [user, setUser] = useState<AuthUser | null>(null);

  // On mount — check if GitHub just redirected back with token in URL params
  useEffect(() => {
    const params   = new URLSearchParams(window.location.search);
    const token    = params.get('token');
    const username = params.get('username');
    const avatar   = params.get('avatar') || '';
    const error    = params.get('error');

    // Always clean the URL
    if (token || error) {
      window.history.replaceState({}, '', window.location.pathname);
    }

    if (error) {
      toast.error('GitHub login failed. Please try again.');
      return;
    }

    if (token && username) {
      setUser({ token, username, avatar });
      toast.success(`Welcome, @${username}! You can now create branches on repos you have access to.`);
    }
  }, []);

  const login  = () => { window.location.href = `${API_URL}/auth/github`; };
  const logout = () => {
    setUser(null);
    toast.info('Logged out.');
  };

  // ── Socket + Agent ──────────────────────────────────────────────────────────
  const { socket, isConnected } = useSocket();
  const { startRun }            = useAgentRun();

  useEffect(() => {
    if (!socket) return;

    socket.on('run_update', (data: any) => {
      if (!data.data) return;
      const { stage, message, progress, result } = data.data;

      setRunData(prev => ({
        ...prev,
        ...(result || {}),
        stage,
        progress,
        message,
      }));

      switch (stage) {
        case 'results_ready':
          setIsRunning(false);
          setIsCIWatching(true);
          toast.success('Fixes applied! CI/CD monitoring running in background...');
          break;
        case 'ci_watching_complete':
          setIsCIWatching(false);
          toast.info(`CI/CD: ${result?.final_cicd_status?.toUpperCase() || 'UNKNOWN'}`);
          break;
        case 'completed':
          setIsRunning(false);
          setIsCIWatching(false);
          toast.success('🎉 Agent run complete!');
          break;
        case 'error':
          setIsRunning(false);
          setIsCIWatching(false);
          toast.error(`Error: ${message}`);
          break;
      }
    });

    return () => { socket.off('run_update'); };
  }, [socket]);

  // ── Start run ───────────────────────────────────────────────────────────────
  const handleStartRun = async (repoUrl: string, teamName: string, teamLeader: string) => {
    setIsRunning(true);
    setIsCIWatching(false);
    setRunData(null);
    setSelectedFix(null);
    setActiveTab('overview');

    try {
      // Pass user's OAuth token — backend will use it to push to original repo
      const result = await startRun(
  repoUrl,
  teamName,
  teamLeader,
  5,                      // ← max_iterations
  user?.token || null     // ← githubToken
);
      if (result.run_id && socket) {
        socket.emit('subscribe_run', { run_id: result.run_id });
      }

      toast.success('Agent run started!');
    } catch (error) {
      toast.error('Failed to start agent run');
      setIsRunning(false);
    }
  };

  const showResults = !!(runData?.fixes || runData?.applied_fixes);

  return (
    <ThemeProvider defaultTheme="dark" storageKey="rift-theme">
      <RunContext.Provider value={{
        runData, isRunning, isCIWatching,
        selectedFix, setSelectedFix,
        user, login, logout,
      }}>
        <div className="min-h-screen bg-background">

          {/* Header — pass auth props so it can show login button */}
          <Header
            isConnected={isConnected}
            authSlot={
              <GitHubLoginButton user={user} onLogin={login} onLogout={logout} />
            }
          />

          <main className="container mx-auto px-4 py-6 space-y-6">

            {/* Warning if not logged in */}
            {!user && (
              <div className="flex items-center gap-3 p-3 rounded-lg border border-yellow-500/30 bg-yellow-500/5 text-yellow-400 text-sm">
                <span>⚠</span>
                <span>
                  Login with GitHub so the agent can create branches and PRs on your behalf.
                  Without login, a server token will be used (if configured).
                </span>
                <button
                  onClick={login}
                  className="ml-auto text-xs underline hover:text-yellow-300"
                >
                  Login →
                </button>
              </div>
            )}

            {/* Input Section */}
            <InputSection onStartRun={handleStartRun} isRunning={isRunning} />

            {/* Live Architecture */}
            {isRunning && (
              <LiveArchitecture
                stage={runData?.stage || 'initializing'}
                progress={runData?.progress || 0}
              />
            )}

            {/* Results Tabs */}
            {showResults && (
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-6">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="fixes">
                    Fixes
                    {runData?.applied_fixes?.length ? (
                      <span className="ml-1.5 text-xs bg-primary text-primary-foreground rounded-full px-1.5">
                        {runData.applied_fixes.length}
                      </span>
                    ) : null}
                  </TabsTrigger>
                  <TabsTrigger value="cicd">
                    CI/CD
                    {isCIWatching && (
                      <span className="ml-1.5 text-xs bg-yellow-500 text-black rounded-full px-1.5 animate-pulse">
                        Live
                      </span>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="tree">File Tree</TabsTrigger>
                  <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
                  <TabsTrigger value="history">History</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <RunSummaryCard runData={runData} />
                    <ScoreBreakdownPanel score={runData?.score} />
                  </div>
                </TabsContent>

                <TabsContent value="fixes">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <FixesTable fixes={runData?.fixes || runData?.applied_fixes || []} />
                    {selectedFix && <CodeDiffViewer fix={selectedFix} />}
                  </div>
                </TabsContent>

                <TabsContent value="cicd">
                  {isCIWatching && (!runData?.cicd_iterations || runData.cicd_iterations.length === 0) ? (
                    <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                      <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-4" />
                      <p className="text-sm font-medium">Monitoring CI/CD pipeline...</p>
                      <p className="text-xs mt-1 opacity-60">Other tabs are fully available.</p>
                    </div>
                  ) : (
                    <CICDTimeline
                      iterations={runData?.cicd_iterations || []}
                      finalStatus={runData?.final_cicd_status}
                    />
                  )}
                </TabsContent>

                <TabsContent value="tree">
                  <RepositoryTree
                    tree={runData?.file_tree}
                    fixes={runData?.fixes || runData?.applied_fixes || []}
                  />
                </TabsContent>

                <TabsContent value="heatmap">
                  <BugHeatmap fixes={runData?.fixes || runData?.applied_fixes || []} />
                </TabsContent>

                <TabsContent value="history">
                  <HistoricalRuns />
                </TabsContent>
              </Tabs>
            )}
          </main>

          <Toaster />
        </div>
      </RunContext.Provider>
    </ThemeProvider>
  );
}

export default App;