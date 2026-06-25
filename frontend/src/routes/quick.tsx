import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { FlashcardReview } from "@/components/FlashcardReview";
import { useStore } from "@/lib/store";
import { Zap } from "lucide-react";

export const Route = createFileRoute("/quick")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => <AppLayout><Page /></AppLayout>,
});

function Page() {
  const { state } = useStore();
  const cards = state.cards
    .filter((c) => !c.known && (c.difficulty === "Hard" || c.priority === "High" || c.notKnownCount > 0))
    .sort((a, b) => b.notKnownCount - a.notKnownCount);

  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-3xl mx-auto space-y-6">
      <div className="rounded-3xl bg-gradient-primary text-white p-6 shadow-elegant flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-white/15 backdrop-blur flex items-center justify-center"><Zap className="w-6 h-6" /></div>
        <div>
          <h1 className="font-display font-bold text-2xl">⚡ Quick Revision</h1>
          <p className="text-sm text-white/85">Only hard, recently incorrect, and high-priority cards.</p>
        </div>
      </div>
      <FlashcardReview cards={cards} />
    </div>
  );
}
