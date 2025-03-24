import { Outlet, Navigate } from 'react-router-dom'
import { useAtom } from 'jotai'
import { isLoggedInAtom } from '@/store/auth'
import { Sun, Moon, Computer } from 'lucide-react'
import { useTheme } from '@/components/theme-provider'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const AuthLayout = () => {
  const [isLoggedIn] = useAtom(isLoggedInAtom)
  const { theme, setTheme } = useTheme()
  
  // Redirect to dashboard if already logged in
  if (isLoggedIn) {
    return <Navigate to="/" replace />
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="h-16 flex items-center justify-between px-4 lg:px-8 border-b">
        <h1 className="text-xl font-bold">Construction AI Platform</h1>
        
        {/* Theme toggle */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              {theme === 'light' ? (
                <Sun className="h-5 w-5" />
              ) : theme === 'dark' ? (
                <Moon className="h-5 w-5" />
              ) : (
                <Computer className="h-5 w-5" />
              )}
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme('light')}>
              <Sun className="mr-2 h-4 w-4" />
              <span>Light</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme('dark')}>
              <Moon className="mr-2 h-4 w-4" />
              <span>Dark</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme('system')}>
              <Computer className="mr-2 h-4 w-4" />
              <span>System</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </header>
      
      {/* Main content */}
      <main className="flex-1 blueprint-background">
        <div className="max-w-md mx-auto px-4 py-8">
          <div className="bg-card p-6 rounded-lg shadow-lg border">
            <Outlet />
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="py-6 px-4 text-center text-sm text-muted-foreground border-t">
        <p>&copy; {new Date().getFullYear()} Construction AI Platform. All rights reserved.</p>
      </footer>
    </div>
  )
}

export default AuthLayout
