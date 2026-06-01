import { useState } from 'react';
import { Play, Loader2, Github, Users, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface InputSectionProps {
  onStartRun: (repoUrl: string, teamName: string, teamLeader: string) => void;
  isRunning: boolean;
}

export function InputSection({ onStartRun, isRunning }: InputSectionProps) {
  const [repoUrl, setRepoUrl] = useState('');
  const [teamName, setTeamName] = useState('');
  const [teamLeader, setTeamLeader] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (repoUrl && teamName && teamLeader && !isRunning) {
      onStartRun(repoUrl, teamName, teamLeader);
    }
  };

  const isValid = repoUrl && teamName && teamLeader;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Github className="h-5 w-5" />
          Repository Configuration
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Repository URL */}
            <div className="space-y-2">
              <Label htmlFor="repo-url">
                GitHub Repository URL
              </Label>
              <div className="relative">
                <Github className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="repo-url"
                  placeholder="https://github.com/user/repo"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  className="pl-10"
                  disabled={isRunning}
                />
              </div>
            </div>

            {/* Team Name */}
            <div className="space-y-2">
              <Label htmlFor="team-name">
                Team Name
              </Label>
              <div className="relative">
                <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="team-name"
                  placeholder="e.g., RIFT ORGANISERS"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  className="pl-10"
                  disabled={isRunning}
                />
              </div>
            </div>

            {/* Team Leader */}
            <div className="space-y-2">
              <Label htmlFor="team-leader">
                Team Leader Name
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="team-leader"
                  placeholder="e.g., Saiyam Kumar"
                  value={teamLeader}
                  onChange={(e) => setTeamLeader(e.target.value)}
                  className="pl-10"
                  disabled={isRunning}
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            disabled={!isValid || isRunning}
          >
            {isRunning ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Agent Running...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Run Agent
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
