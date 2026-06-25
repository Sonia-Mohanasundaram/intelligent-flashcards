import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Sparkles, ArrowRight, BookOpen, Brain, Zap } from "lucide-react";
import { useEffect } from "react";
import { useStore } from "@/lib/store";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "intelligent-flashcards" },
      { name: "description", content: "Convert study notes into AI-generated flashcards." },
    ],
  }),
  component: Splash,
});

function Splash() {
  const { state } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", state.theme === "dark");
  }, [state.theme]);

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Animated blobs */}
      <div className="absolute inset-0 bg-aurora opacity-70" />
      <div className="absolute top-10 -left-32 w-96 h-96 rounded-full bg-primary/30 blur-3xl animate-blob" />
      <div className="absolute top-40 -right-32 w-96 h-96 rounded-full bg-accent/40 blur-3xl animate-blob" style={{ animationDelay: "3s" }} />
      <div className="absolute bottom-0 left-1/3 w-96 h-96 rounded-full bg-chart-5/30 blur-3xl animate-blob" style={{ animationDelay: "6s" }} />

      <div className="relative z-10 min-h-screen flex flex-col">
        <header className="px-6 lg:px-12 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-bold text-lg">Smart Flashcard AI</span>
          </div>
          <Link to="/auth" className="text-sm font-medium hover:text-primary transition-colors">Sign in</Link>
        </header>

        <main className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="max-w-3xl text-center animate-fade-up">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass mb-8 text-xs font-medium">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              Powered by spaCy & Hugging Face
            </div>
            <div className="text-6xl mb-6 animate-float">📚</div>
            <h1 className="font-display text-5xl md:text-7xl font-extrabold leading-tight mb-4">
              <span className="gradient-text">Smart Flashcard AI</span>
            </h1>
            <p className="text-xl md:text-2xl font-medium mb-3">Learn Smarter with AI</p>
            <p className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
              Convert your study notes into intelligent AI-generated flashcards and revise more effectively.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-3 mb-16">
              <button
                onClick={() => navigate({ to: "/auth" })}
                className="group inline-flex items-center gap-2 rounded-2xl bg-gradient-primary px-7 py-3.5 text-sm font-semibold text-white shadow-elegant hover:shadow-glow transition-all"
              >
                Get Started
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </button>
              <a href="#features" className="inline-flex items-center gap-2 rounded-2xl glass px-7 py-3.5 text-sm font-semibold hover:bg-card transition-colors">
                Learn More
              </a>
            </div>

            <div id="features" className="grid sm:grid-cols-3 gap-4 text-left">
              {[
                { icon: BookOpen, title: "Smart Notes", desc: "Paste any notes and extract the essentials instantly." },
                { icon: Brain, title: "AI Insights", desc: "Get summaries, keywords, entities, and difficulty scoring." },
                { icon: Zap, title: "Quick Revision", desc: "Spaced repetition and intelligent review." },
              ].map((f) => (
                <div key={f.title} className="rounded-2xl glass p-5 hover:shadow-elegant transition-shadow">
                  <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center mb-3">
                    <f.icon className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-display font-bold text-base mb-1">{f.title}</h3>
                  <p className="text-sm text-muted-foreground">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
