import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { useStore } from "@/lib/store";
import { Moon, Sun } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => <AppLayout><Page /></AppLayout>,
});

function Page() {
  const { state, setTheme } = useStore();

  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-3xl mx-auto space-y-6">
      <header>
        <h1 className="font-display font-bold text-3xl">⚙️ Settings</h1>
        <p className="text-sm text-muted-foreground">Customize your Smart Flashcard AI experience.</p>
      </header>

      <section className="rounded-3xl bg-card border border-border p-6 shadow-soft">
        <h3 className="font-display font-bold text-lg mb-4">Theme</h3>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setTheme("light")}
            className={`rounded-2xl p-5 border text-left transition-all ${state.theme === "light" ? "border-primary shadow-elegant ring-2 ring-ring/40" : "border-border hover:bg-accent/40"}`}
          >
            <Sun className="w-5 h-5 mb-2" />
            <div className="font-semibold">Light</div>
            <div className="text-xs text-muted-foreground">Bright and airy</div>
          </button>
          <button
            onClick={() => setTheme("dark")}
            className={`rounded-2xl p-5 border text-left transition-all ${state.theme === "dark" ? "border-primary shadow-elegant ring-2 ring-ring/40" : "border-border hover:bg-accent/40"}`}
          >
            <Moon className="w-5 h-5 mb-2" />
            <div className="font-semibold">Dark</div>
            <div className="text-xs text-muted-foreground">Focused and minimal</div>
          </button>
        </div>
      </section>

      <section className="rounded-3xl bg-card border border-border p-6 shadow-soft">
        <h3 className="font-display font-bold text-lg mb-2">Account</h3>
        <div className="text-sm text-muted-foreground mb-4">Signed in as <b className="text-foreground">{state.user?.email}</b></div>
        <button
          onClick={() => { localStorage.removeItem("smart-flashcard-ai:v1"); toast.success("Local data cleared. Reload to start over."); }}
          className="text-xs px-3 py-2 rounded-lg border border-input hover:bg-destructive/10 hover:text-destructive transition-colors"
        >
          Clear all local data
        </button>
      </section>
    </div>
  );
}
