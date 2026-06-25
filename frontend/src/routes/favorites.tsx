import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { FlashcardReview } from "@/components/FlashcardReview";
import { useStore } from "@/lib/store";

export const Route = createFileRoute("/favorites")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => <AppLayout><Page /></AppLayout>,
});

function Page() {
  const { state } = useStore();
  const cards = state.cards.filter((c) => c.favorite);
  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-3xl mx-auto space-y-6">
      <header>
        <h1 className="font-display font-bold text-3xl">❤️ Favorite Flashcards</h1>
        <p className="text-sm text-muted-foreground">{cards.length} bookmarked cards.</p>
      </header>
      <FlashcardReview cards={cards} />
    </div>
  );
}
