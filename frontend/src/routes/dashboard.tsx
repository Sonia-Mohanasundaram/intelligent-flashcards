import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { AIProcessingPipeline } from "@/components/AIProcessingPipeline";
import { useStore } from "@/lib/store";
import { analyzeNotes, buildSetFromResult, type AIResult } from "@/lib/ai";
import { flashcardAPI } from "@/lib/api";
import { Sparkles, Upload, FileText, Trash2, TrendingUp, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  ),
});

const SAMPLE = `Java is a high-level, class-based, object-oriented programming language developed by Sun Microsystems in 1995. It is designed to have as few implementation dependencies as possible. Java applications are typically compiled to bytecode that can run on any Java Virtual Machine (JVM) regardless of the underlying computer architecture. Core principles of Java include inheritance, polymorphism, encapsulation, and abstraction. These principles allow developers to build robust and reusable software systems.`;

function Dashboard() {
  const { state, addSet } = useStore();
  const navigate = useNavigate();
  const [notes, setNotes] = useState("");
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<AIResult | null>(null);
  const [lastSetId, setLastSetId] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const wordCount = useMemo(() => notes.trim().split(/\s+/).filter(Boolean).length, [notes]);
  const charCount = notes.length;
  const readingMinutes = Math.max(1, Math.ceil(wordCount / 200));

  const knownCount = state.cards.filter((c) => c.known).length;
  const savedCount = state.cards.filter((c) => c.saved).length;

  const handleGenerate = async () => {
    if (!selectedFile && notes.trim().length < 40) {
      toast.error("Please paste at least a few sentences of notes.");
      return;
    }
    
    setProcessing(true);
    setResult(null);
    
    try {
      const title = selectedFile?.name || `Study Notes - ${new Date().toLocaleString()}`;
      const backendResult = selectedFile
        ? await flashcardAPI.generateFromFile(selectedFile, title)
        : await flashcardAPI.generate(notes, title);
      
      // Convert backend result to frontend format
      const frontendResult: AIResult = {
        summary: backendResult.summary || [],
        keywords: backendResult.keywords || [],
        entities: backendResult.entities || [],
        topics: backendResult.topics || [],
        questions: (backendResult.flashcards || []).map((fc: any) => ({
          question: fc.question,
          answer: fc.answer,
          difficulty: fc.difficulty as any
        })),
        topic: backendResult.topic || backendResult.subject || 'General Knowledge',
        subject: backendResult.topic || backendResult.subject || 'General Knowledge',
        difficulty: backendResult.difficulty || 'Medium',
        totalWords: backendResult.wordCount || 0,
      };
      
      const { set, cards } = buildSetFromResult(notes, frontendResult);
      addSet(set, cards);
      setResult(frontendResult);
      setLastSetId(set.id);
      toast.success(`Generated ${cards.length} flashcards successfully!`);
    } catch (error) {
      // Fallback to local processing if backend is not available
      console.warn("Backend unavailable, using local processing:", error);
      toast.info("Processing locally (backend unavailable)");
      
      const r = analyzeNotes(notes);
      const { set, cards } = buildSetFromResult(notes, r);
      addSet(set, cards);
      setResult(r);
      setLastSetId(set.id);
      toast.success(`Generated ${cards.length} flashcards locally!`);
    } finally {
      setProcessing(false);
    }
  };

  const handleFile = (file: File) => {
    if (!/\.(txt|pdf|docx)$/i.test(file.name)) {
      toast.error("Please upload a TXT, PDF, or DOCX file");
      return;
    }
    setSelectedFile(file);
    if (!file.name.endsWith(".txt")) {
      setNotes(`Selected file: ${file.name}`);
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => setNotes(String(e.target?.result ?? ""));
    reader.readAsText(file);
  };

  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-7xl mx-auto space-y-8">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-hero p-6 md:p-10 text-white shadow-elegant animate-fade-up">
        <div className="absolute -top-20 -right-20 w-72 h-72 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-72 h-72 rounded-full bg-white/10 blur-3xl" />
        <div className="relative z-10 flex flex-col gap-6">
        <div>
          <p className="text-sm text-white/80 mb-1">Welcome back,</p>
          <h1 className="font-display text-3xl md:text-4xl font-extrabold">{state.user?.name ?? "Learner"} 👋</h1>
          <p className="text-white/90 mt-1">Paste your notes and generate flashcards fast — no clutter, no unnecessary metrics.</p>
        </div>
      </div>
      </section>

      {/* Quick stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={FileText} label="Flashcard Sets" value={state.sets.length} />
        <StatCard icon={Sparkles} label="Total Cards" value={state.cards.length} />
        <StatCard icon={CheckCircle2} label="Known" value={knownCount} accent="success" />
        <StatCard icon={TrendingUp} label="In Revision" value={savedCount} accent="warning" />
      </section>

      {/* Notes input */}
      <section className="rounded-3xl bg-card border border-border shadow-soft p-6 md:p-8 animate-fade-up">
        <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
          <div>
            <h2 className="font-display font-bold text-xl">Study Notes</h2>
            <p className="text-sm text-muted-foreground">Paste any notes — the AI will craft flashcards for you.</p>
          </div>
          <button
            onClick={() => { setSelectedFile(null); setNotes(SAMPLE); }}
            className="text-xs px-3 py-1.5 rounded-full bg-accent/50 hover:bg-accent transition-colors"
          >
            Try sample notes
          </button>
        </div>

        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Paste your study notes here, or upload TXT ( Note TXT only)..."
          className="w-full min-h-[220px] rounded-2xl bg-background border border-input p-4 text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-ring transition-all resize-y"
        />

        <div className="flex flex-wrap items-center justify-between gap-3 mt-4">
          <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
            <span><b className="text-foreground">{wordCount}</b> words</span>
            <span><b className="text-foreground">{charCount}</b> chars</span>
            <span>~<b className="text-foreground">{readingMinutes}</b> min read</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <label className="inline-flex items-center gap-2 text-xs px-3 py-2 rounded-xl border border-input cursor-pointer hover:bg-accent/50 transition-colors">
              <Upload className="w-3.5 h-3.5" /> Upload Notes
              <input type="file" accept=".txt,.pdf,.docx" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
            </label>
            <button
              onClick={() => { setNotes(""); setSelectedFile(null); setResult(null); }}
              className="inline-flex items-center gap-2 text-xs px-3 py-2 rounded-xl border border-input hover:bg-destructive/10 hover:text-destructive transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" /> Clear
            </button>
            <button
              onClick={handleGenerate}
              disabled={processing}
              className="inline-flex items-center gap-2 text-sm px-5 py-2.5 rounded-xl bg-gradient-primary text-white font-semibold shadow-elegant hover:shadow-glow transition-all disabled:opacity-60"
            >
              <Sparkles className="w-4 h-4" /> Generate Flashcards
            </button>
          </div>
        </div>
      </section>

      {processing && <AIProcessingPipeline onComplete={() => undefined} />}

      {result && lastSetId && (
        <InsightsPanel result={result} setId={lastSetId} onReview={() => navigate({ to: "/review/$setId", params: { setId: lastSetId } })} />
      )}

      {!processing && !result && state.sets.length === 0 && <EmptyState />}

      {state.sets.length > 0 && (
        <section className="rounded-3xl bg-card border border-border p-6 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-bold text-xl">Recent Activity</h2>
          </div>
          <ul className="divide-y divide-border">
            {state.sets.slice(0, 5).map((s) => (
              <li key={s.id} className="py-3 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="font-medium truncate">{s.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {(s as any).topic || s.subject} · {s.flashcardIds.length} cards · {new Date(s.createdAt).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={() => navigate({ to: "/review/$setId", params: { setId: s.id } })}
                  className="text-xs px-3 py-1.5 rounded-lg bg-gradient-primary text-white font-medium shadow-soft"
                >
                  Review
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function HeroStat({ icon: Icon, label, value }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white/15 backdrop-blur border border-white/20 px-4 py-3">
      <Icon className="w-4 h-4 mb-1 text-white/90" />
      <div className="text-xl font-display font-bold">{value}</div>
      <div className="text-xs text-white/80">{label}</div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, accent }: {
  icon: React.ComponentType<{ className?: string }>; label: string; value: number;
  accent?: "success" | "warning";
}) {
  const accentClass = accent === "success" ? "from-success to-success" : accent === "warning" ? "from-warning to-warning" : "";
  return (
    <div className="rounded-2xl bg-card border border-border p-5 shadow-soft hover:shadow-elegant transition-shadow">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${accent ? `bg-gradient-to-br ${accentClass}` : "bg-gradient-primary"}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div className="text-2xl font-display font-bold">{value}</div>
      <div className="text-xs text-muted-foreground">{label}</div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-3xl bg-card border border-border p-12 text-center shadow-soft">
      <div className="text-6xl mb-3 animate-float">🗂️</div>
      <h3 className="font-display font-bold text-xl mb-1">No flashcards yet.</h3>
      <p className="text-sm text-muted-foreground">Paste your study notes to generate your first AI flashcards.</p>
    </div>
  );
}

function InsightsPanel({ result, setId, onReview }: { result: AIResult; setId: string; onReview: () => void }) {
  return (
    <div className="space-y-6 animate-fade-up">
      <div className="rounded-3xl bg-card border border-border p-6 md:p-8 shadow-elegant">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
          <div>
            <h3 className="font-display font-bold text-lg">AI Insights</h3>
            <p className="text-xs text-muted-foreground">Topic: <b className="text-foreground">{result.topic || result.subject}</b></p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Insight label="Total Words" value={`${result.totalWords}`} />
          <Insight label="Questions Generated" value={`${result.questions.length}`} />
          <Insight label="Topic" value={result.topic || result.subject} />
          <Insight label="Keywords" value={`${result.keywords.length}`} />
        </div>
      </div>

      <div className="rounded-3xl bg-card border border-border p-6 md:p-8 shadow-soft">
        <h3 className="font-display font-bold text-lg mb-4">📝 AI Summary</h3>
        <ul className="space-y-2">
          {result.summary.map((s, i) => (
            <li key={i} className="flex gap-3 text-sm leading-relaxed">
              <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-gradient-primary flex-shrink-0" />
              <span>{s}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="rounded-3xl bg-card border border-border p-6 shadow-soft">
        <h3 className="font-display font-bold text-lg mb-4">🔑 Keywords</h3>
        <div className="flex flex-wrap gap-2">
          {result.keywords.map((k) => (
            <span key={k} className="px-3 py-1.5 rounded-full text-xs font-medium bg-gradient-to-r from-primary/10 to-accent/30 border border-border hover:scale-105 transition-transform cursor-default">
              {k}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-3xl bg-gradient-primary text-white p-6 md:p-8 shadow-elegant flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="text-sm text-white/80">✅ Flashcards Generated Successfully</div>
          <div className="font-display font-bold text-2xl mt-1">{result.questions.length} cards created</div>
        </div>
        <button onClick={onReview} className="rounded-xl bg-white text-primary px-5 py-2.5 text-sm font-semibold shadow-soft hover:shadow-glow transition-all">
          Start Reviewing →
        </button>
      </div>
    </div>
  );
}

function Insight({ label, value, badgeClass }: { label: string; value: string; badgeClass?: string }) {
  return (
    <div className="rounded-2xl bg-accent/20 p-4">
      <div className="text-xs text-muted-foreground mb-1">{label}</div>
      <div className={`inline-block font-semibold ${badgeClass ? `px-2.5 py-1 rounded-lg text-sm ${badgeClass}` : "text-lg"}`}>{value}</div>
    </div>
  );
}
