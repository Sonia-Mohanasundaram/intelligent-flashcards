import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import {
  Home, History, Bookmark, Heart, CheckCircle2, BarChart3, Zap, Settings, LogOut, Menu, X, Moon, Sun, Sparkles,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { useStore } from "@/lib/store";
import { Button } from "@/components/ui/button";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: Home },
  { to: "/history", label: "History", icon: History },
  { to: "/saved", label: "Saved for Revision", icon: Bookmark },
  { to: "/favorites", label: "Favorites", icon: Heart },
  { to: "/known", label: "Known Cards", icon: CheckCircle2 },
  { to: "/statistics", label: "Statistics", icon: BarChart3 },
  { to: "/quick", label: "Quick Revision", icon: Zap },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppLayout({ children }: { children: ReactNode }) {
  const { state, setUser, toggleTheme } = useStore();
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [open, setOpen] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(true);
    const raw = typeof window !== "undefined" ? localStorage.getItem("smart-flashcard-ai:v1") : null;
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (!parsed.user) navigate({ to: "/auth" });
      } catch {
        navigate({ to: "/auth" });
      }
    } else {
      navigate({ to: "/auth" });
    }
  }, [navigate]);

  if (!ready) return null;

  const handleLogout = () => {
    setUser(null);
    navigate({ to: "/" });
  };

  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen z-40 w-72 bg-sidebar border-r border-sidebar-border transition-transform duration-300 flex flex-col ${
          open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-display font-bold text-base leading-tight">Smart Flashcard</div>
            <div className="text-xs text-muted-foreground">AI Learning</div>
          </div>
        </div>

        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          {NAV.map((item) => {
            const active = pathname === item.to || (item.to !== "/dashboard" && pathname.startsWith(item.to));
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setOpen(false)}
                className={`group flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  active
                    ? "bg-gradient-primary text-white shadow-elegant"
                    : "text-sidebar-foreground hover:bg-sidebar-accent"
                }`}
              >
                <Icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${active ? "" : "text-muted-foreground"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-sidebar-border space-y-2">
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-sidebar-accent/50">
            <div className="w-9 h-9 rounded-full bg-gradient-primary flex items-center justify-center text-white font-semibold text-sm">
              {state.user?.name.charAt(0).toUpperCase() ?? "U"}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{state.user?.name ?? "Guest"}</div>
              <div className="text-xs text-muted-foreground truncate">{state.user?.email ?? ""}</div>
            </div>
          </div>
          <Button variant="ghost" className="w-full justify-start gap-3" onClick={handleLogout}>
            <LogOut className="w-4 h-4" /> Logout
          </Button>
        </div>
      </aside>

      {open && (
        <div className="fixed inset-0 bg-black/40 z-30 lg:hidden" onClick={() => setOpen(false)} />
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-20 h-16 glass border-b border-border flex items-center justify-between px-4 lg:px-8">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(!open)}>
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
            <div className="hidden md:flex items-center gap-2 text-sm text-muted-foreground">
              <Sparkles className="w-4 h-4 text-primary" />
              <span>AI-Powered Study Companion</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
              {state.theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
          </div>
        </header>

        <main className="flex-1 overflow-x-hidden">{children}</main>
      </div>
    </div>
  );
}
