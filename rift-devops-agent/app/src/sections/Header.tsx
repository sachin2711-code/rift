// import { GitBranch, Moon, Sun, Activity } from 'lucide-react';
// import { useTheme } from '@/components/theme-provider';
// import { Button } from '@/components/ui/button';
// import { Badge } from '@/components/ui/badge';

// interface HeaderProps {
//   isConnected: boolean;
// }

// export function Header({ isConnected }: HeaderProps) {
//   const { theme, setTheme } = useTheme();

//   return (
//     <header className="border-b bg-card">
//       <div className="container mx-auto px-4 py-4">
//         <div className="flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <div className="p-2 bg-primary rounded-lg">
//               <GitBranch className="h-6 w-6 text-primary-foreground" />
//             </div>
//             <div>
//               <h1 className="text-xl font-bold">RIFT DevOps Agent</h1>
//               <p className="text-sm text-muted-foreground">
//                 Autonomous CI/CD Healing
//               </p>
//             </div>
//           </div>

//           <div className="flex items-center gap-4">
//             {/* Connection Status */}
//             <Badge 
//               variant={isConnected ? "default" : "destructive"}
//               className="flex items-center gap-1"
//             >
//               <Activity className="h-3 w-3" />
//               {isConnected ? 'Connected' : 'Disconnected'}
//             </Badge>

//             {/* Theme Toggle */}
//             <Button
//               variant="ghost"
//               size="icon"
//               onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
//             >
//               {theme === 'dark' ? (
//                 <Sun className="h-5 w-5" />
//               ) : (
//                 <Moon className="h-5 w-5" />
//               )}
//             </Button>
//           </div>
//         </div>
//       </div>
//     </header>
//   );
// }
import { GitBranch, Moon, Sun, Activity } from 'lucide-react';
import { useTheme } from '@/components/theme-provider';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface HeaderProps {
  isConnected: boolean;
  authSlot?: React.ReactNode;  // ← ADDED
}

export function Header({ isConnected, authSlot }: HeaderProps) {
  const { theme, setTheme } = useTheme();

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg">
              <GitBranch className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">RIFT DevOps Agent</h1>
              <p className="text-sm text-muted-foreground">
                Autonomous CI/CD Healing
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <Badge
              variant={isConnected ? "default" : "destructive"}
              className="flex items-center gap-1"
            >
              <Activity className="h-3 w-3" />
              {isConnected ? 'Connected' : 'Disconnected'}
            </Badge>

            {/* GitHub Login Button — injected from App.tsx */}
            {authSlot}  {/* ← ADDED */}

            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
