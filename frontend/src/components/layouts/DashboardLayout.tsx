import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { useAtom } from 'jotai'
import { userAtom, logoutAtom } from '@/store/auth'
import { 
  LayoutDashboard, FileText, FileUp, Calculator, 
  PuzzlePiece, Settings, ChevronDown, Menu, X, LogOut,
  Sun, Moon, Computer
} from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useTheme } from '@/components/theme-provider'
import { NavLink } from 'react-router-dom'

const DashboardLayout = () => {
  const [user] = useAtom(userAtom)
  const [, logout] = useAtom(logoutAtom)
  const { theme, setTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  
  // Navigation items
  const navItems = [
    { 
      name: 'Dashboard', 
      path: '/', 
      icon: <LayoutDashboard className="h-5 w-5" /> 
    },
    { 
      name: 'Projects', 
      path: '/projects', 
      icon: <FileText className="h-5 w-5" /> 
    },
    { 
      name: 'Documents', 
      path: '/documents', 
      icon: <FileUp className="h-5 w-5" /> 
    },
    { 
      name: 'Estimations', 
      path: '/estimations', 
      icon: <Calculator className="h-5 w-5" /> 
    },
    { 
      name: 'Plugins', 
      path: '/plugins', 
      icon: <PuzzlePiece className="h-5 w-5" /> 
    },
    { 
      name: 'Settings', 
      path: '/settings', 
      icon: <Settings className="h-5 w-5" /> 
    }
  ]
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background border-b h-16 flex items-center justify-between px-4 lg:px-8">
        <div className="flex items-center">
          <Button variant="ghost" size="icon" onClick={toggleSidebar} className="lg:hidden mr-2">
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <h1 className="text-xl font-bold">Construction AI Platform</h1>
        </div>
        
        <div className="flex items-center space-x-4">
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
          
          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center">
                <span className="mr-2">{user?.full_name}</span>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => logout()}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Logout</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside 
          className={cn(
            "bg-muted/40 border-r w-64 shrink-0 overflow-y-auto transition-all",
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0 lg:w-20",
            "fixed inset-y-0 top-16 lg:static z-40"
          )}
        >
          <nav className="p-4 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => cn(
                  "flex items-center py-2 px-3 rounded-md transition-colors",
                  "hover:bg-accent hover:text-accent-foreground",
                  isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground",
                  !sidebarOpen && "lg:justify-center"
                )}
              >
                {item.icon}
                {(sidebarOpen || window.innerWidth < 1024) && (
                  <span className="ml-3">{item.name}</span>
                )}
              </NavLink>
            ))}
          </nav>
        </aside>
        
        {/* Main content */}
        <main 
          className={cn(
            "flex-1 overflow-y-auto p-4 lg:p-8",
            sidebarOpen ? "lg:ml-0" : "lg:ml-0"
          )}
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
