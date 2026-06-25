import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { FlashcardReview } from "@/components/FlashcardReview";
import { useStore } from "@/lib/store";

export const Route = createFileRoute("/review/$setId")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => <AppLayout><Review /></AppLayout>,
});

function Review() {
  const { setId } = Route.useParams();
  const { state } = useStore();
  const set = state.sets.find((s) => s.id === setId);
  const cards = state.cards.filter((c) => c.setId === setId);

  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-3xl mx-auto space-y-6">
      <header>
        <h1 className="font-display font-bold text-3xl">{set?.title ?? "Review"}</h1>
        <p className="text-sm text-muted-foreground">{(set as any)?.topic || set?.subject} · {cards.length} cards</p>
      </header>
      <FlashcardReview cards={cards} />
    </div>
  );
}
