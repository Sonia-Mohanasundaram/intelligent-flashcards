import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { useStore } from "@/lib/store";
import { Search, Download, Copy, Pencil, Trash2, Play } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/history")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => <AppLayout><HistoryPage /></AppLayout>,
});

function HistoryPage() {
  const { state, deleteSet, duplicateSet, renameSet } = useStore();
  const navigate = useNavigate();
  const [q, setQ] = useState("");

  const filtered = useMemo(() => {
    const term = q.toLowerCase();
    if (!term) return state.sets;
    return state.sets.filter((s) => {
      if (s.title.toLowerCase().includes(term)) return true;
      if ((s as any).topic?.toLowerCase().includes(term)) return true;
      if (s.subject.toLowerCase().includes(term)) return true;
      if (s.keywords.some((k) => k.toLowerCase().includes(term))) return true;
      const cards = state.cards.filter((c) => c.setId === s.id);
      return cards.some((c) => c.question.toLowerCase().includes(term) || c.answer.toLowerCase().includes(term));
    });
  }, [q, state.sets, state.cards]);

  const exportSet = (id: string, format: "json" | "csv") => {
    const set = state.sets.find((s) => s.id === id);
    if (!set) return;
    const cards = state.cards.filter((c) => c.setId === id);
    let blob: Blob;
    let filename: string;
    if (format === "json") {
      blob = new Blob([JSON.stringify({ set, cards }, null, 2)], { type: "application/json" });
      filename = `${set.title}.json`;
    } else {
      const rows = [["Question","Answer","Difficulty"], ...cards.map((c) => [c.question, c.answer, c.difficulty])];
      blob = new Blob([rows.map((r) => r.map((x) => `"${x.replace(/"/g, '""')}"`).join(",")).join("\n")], { type: "text/csv" });
      filename = `${set.title}.csv`;
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
    toast.success("Export completed");
  };

  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="font-display font-bold text-3xl">History</h1>
        <p className="text-sm text-muted-foreground">All your AI-generated flashcard sets, newest first.</p>
      </header>

      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by title, question, answer, keyword, topic..."
          className="w-full rounded-2xl bg-card border border-input pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-3xl bg-card border border-border p-12 text-center">
          <div className="text-5xl mb-2">🗂️</div>
          <p className="text-muted-foreground">No sets match your search.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {filtered.map((s) => (
            <div key={s.id} className="rounded-2xl bg-card border border-border p-5 shadow-soft hover:shadow-elegant transition-shadow">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="min-w-0">
                  <h3 className="font-display font-bold text-base truncate">{s.title}</h3>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {(s as any).topic || s.subject} · {s.flashcardIds.length} cards · {new Date(s.createdAt).toLocaleDateString()}
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-lg ${s.difficulty === "Hard" ? "bg-destructive/10 text-destructive" : s.difficulty === "Medium" ? "bg-warning/10" : "bg-success/10 text-success"}`}>
                  {s.difficulty}
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 mb-4">
                {s.keywords.slice(0, 5).map((k) => (
                  <span key={k} className="text-xs px-2 py-0.5 rounded-full bg-accent/40">{k}</span>
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => navigate({ to: "/review/$setId", params: { setId: s.id } })} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-gradient-primary text-white font-medium">
                  <Play className="w-3.5 h-3.5" /> Open
                </button>
                <button onClick={() => {
                  const t = prompt("Rename set:", s.title);
                  if (t) renameSet(s.id, t);
                }} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-input hover:bg-accent/40">
                  <Pencil className="w-3.5 h-3.5" /> Rename
                </button>
                <button onClick={() => { duplicateSet(s.id); toast.success("Duplicated"); }} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-input hover:bg-accent/40">
                  <Copy className="w-3.5 h-3.5" /> Duplicate
                </button>
                <button onClick={() => exportSet(s.id, "json")} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-input hover:bg-accent/40">
                  <Download className="w-3.5 h-3.5" /> JSON
                </button>
                <button onClick={() => exportSet(s.id, "csv")} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-input hover:bg-accent/40">
                  <Download className="w-3.5 h-3.5" /> CSV
                </button>
                <button onClick={() => { if (confirm("Delete this set?")) { deleteSet(s.id); toast.success("Deleted"); } }} className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-input text-destructive hover:bg-destructive/10">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
