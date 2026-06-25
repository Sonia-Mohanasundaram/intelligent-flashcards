import { useEffect, useState } from "react";
import { Check, Loader2 } from "lucide-react";

export const PIPELINE_STEPS = [
  "Notes Received",
  "Cleaning Text",
  "Removing Stopwords",
  "Tokenizing",
  "Extracting Keywords",
  "Extracting Named Entities",
  "Ranking Important Sentences",
  "Generating Summary",
  "Generating Questions",
  "Generating Answers",
  "Saving Flashcards",
  "Completed Successfully",
];

export function AIProcessingPipeline({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (step >= PIPELINE_STEPS.length) {
      const t = setTimeout(onComplete, 600);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setStep((s) => s + 1), 250);
    return () => clearTimeout(t);
  }, [step, onComplete]);

  return (
    <div className="rounded-3xl glass shadow-elegant p-6 md:p-8 animate-scale-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow">
          <Loader2 className="w-5 h-5 text-white animate-spin" />
        </div>
        <div>
          <h3 className="font-display font-bold text-lg">AI Processing Pipeline</h3>
          <p className="text-xs text-muted-foreground">Local spaCy + t5-small processing</p>
        </div>
      </div>
      
      <div className="mb-4 px-4 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
        <p className="text-sm text-blue-600 font-medium">
          Step {Math.min(step + 1, PIPELINE_STEPS.length)} of {PIPELINE_STEPS.length}
        </p>
      </div>

      <ol className="space-y-2 max-h-96 overflow-y-auto">
        {PIPELINE_STEPS.map((label, i) => {
          const done = i < step;
          const active = i === step;
          return (
            <li
              key={label}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all duration-200 ${
                done
                  ? "border-success/30 bg-success/5"
                  : active
                  ? "border-primary/40 bg-primary/5 shadow-soft"
                  : "border-border/60 opacity-50"
              }`}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0 ${
                  done
                    ? "bg-success text-success-foreground"
                    : active
                    ? "bg-gradient-primary text-white animate-pulse-ring"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {done ? <Check className="w-4 h-4" /> : active ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : i + 1}
              </div>
              <span className={`text-sm font-medium ${done || active ? "" : "text-muted-foreground"}`}>{label}</span>
            </li>
          );
        })}
      </ol>
      
      <div className="mt-6 pt-4 border-t border-border/50">
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-border/30 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-primary rounded-full transition-all duration-300"
              style={{ width: `${(step / PIPELINE_STEPS.length) * 100}%` }}
            />
          </div>
          <span className="text-xs text-muted-foreground font-medium">{Math.round((step / PIPELINE_STEPS.length) * 100)}%</span>
        </div>
      </div>
    </div>
  );
}
