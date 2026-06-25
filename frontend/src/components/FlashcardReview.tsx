import { useEffect, useState } from "react";
import { Heart, Bookmark, CheckCircle2, Trash2, ChevronLeft, ChevronRight, RotateCw, Volume2, VolumeX, ArrowLeft } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import type { Flashcard } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { useStore } from "@/lib/store";
import { toast } from "sonner";

const MUTE_STORAGE_KEY = "smart-flashcard-ai:mute-speech";

export function FlashcardReview({ cards }: { cards: Flashcard[] }) {
  const navigate = useNavigate();
  const { updateCard, deleteCard } = useStore();
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [isMuted, setIsMuted] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem(MUTE_STORAGE_KEY) === "true";
  });
  const [isSpeaking, setIsSpeaking] = useState(false);
  const speechSupported = typeof window !== "undefined" && typeof window.speechSynthesis !== "undefined" && typeof window.SpeechSynthesisUtterance !== "undefined";

  if (!cards.length) {
    return (
      <div className="rounded-3xl glass p-12 text-center">
        <div className="text-5xl mb-3">🗂️</div>
        <h3 className="font-display font-bold text-xl">No flashcards here</h3>
        <p className="text-sm text-muted-foreground mt-1">Generate some from your notes to start reviewing.</p>
      </div>
    );
  }

  const card = cards[Math.min(index, cards.length - 1)];
  const progress = ((index + 1) / cards.length) * 100;

  const next = () => {
    setFlipped(false);
    setTimeout(() => setIndex((i) => Math.min(i + 1, cards.length - 1)), 150);
  };
  const prev = () => {
    setFlipped(false);
    setTimeout(() => setIndex((i) => Math.max(i - 1, 0)), 150);
  };

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(MUTE_STORAGE_KEY, isMuted ? "true" : "false");
  }, [isMuted]);

  useEffect(() => {
    if (!speechSupported) return;
    const synth = window.speechSynthesis;
    synth.cancel();
    setIsSpeaking(false);

    if (!flipped || isMuted) return;

    const utterance = new SpeechSynthesisUtterance(card.answer);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synth.speak(utterance);

    return () => {
      if (synth.speaking || synth.pending) {
        synth.cancel();
      }
    };
  }, [card.answer, flipped, isMuted, speechSupported]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">Flashcard {index + 1} of {cards.length}</span>
        <span className="text-muted-foreground">{Math.round(progress)}% complete</span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div className="h-full bg-gradient-primary transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>

      <div
        className={`flip-card ${flipped ? "flipped" : ""} cursor-pointer select-none`}
        onClick={() => setFlipped((f) => !f)}
      >
        <div className="flip-card-inner relative w-full min-h-[340px] md:min-h-[400px]">
          <div className="flip-card-front absolute inset-0 rounded-3xl bg-gradient-hero p-10 flex flex-col justify-between shadow-elegant text-white">
            <div className="flex items-center justify-between text-xs uppercase tracking-wider text-white/70">
              <span>Question</span>
              <span className="px-2 py-0.5 rounded-full bg-white/15 backdrop-blur">{card.difficulty}</span>
            </div>
            <div className="flex-1 flex items-center justify-center text-center">
              <h2 className="font-display font-bold text-2xl md:text-3xl leading-tight">{card.question}</h2>
            </div>
            <div className="flex items-center justify-center gap-2 text-xs text-white/80">
              <RotateCw className="w-3.5 h-3.5" /> Tap card to flip
            </div>
          </div>
          <div className="flip-card-back absolute inset-0 rounded-3xl bg-emerald-50 border border-emerald-200 p-10 flex flex-col justify-between shadow-elegant overflow-hidden text-emerald-950">
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-xs uppercase tracking-[0.35em] text-emerald-700 font-semibold">
                <span className="block h-0.5 w-10 rounded-full bg-emerald-600" />
                <span>Answer</span>
              </div>
              <div className="rounded-3xl bg-emerald-100/80 px-4 py-3 inline-flex items-center gap-2 text-sm font-semibold text-emerald-900 shadow-sm border border-emerald-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                Ready to review
              </div>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 px-4">
              <p className="text-2xl md:text-3xl font-semibold leading-tight text-emerald-950">{card.answer}</p>
              <p className="text-sm text-emerald-700/90 max-w-2xl">
                {speechSupported
                  ? isMuted
                    ? "Voice playback is muted. Unmute to hear the answer when the card flips."
                    : isSpeaking
                      ? "Reading answer aloud..."
                      : "Answer will be read aloud when this side appears."
                  : "Browser speech synthesis not supported on this device."}
              </p>
            </div>
            <div className="flex items-center justify-center gap-2 text-xs text-emerald-700">
              <RotateCw className="w-3.5 h-3.5" /> Tap card to flip back
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 justify-center">
        <Button variant="outline" onClick={() => navigate({ to: "/dashboard" })}>
          <ArrowLeft className="w-4 h-4" /> Dashboard
        </Button>
        {speechSupported && (
          <Button
            variant={isMuted ? "default" : "outline"}
            onClick={(e) => {
              e.stopPropagation();
              setIsMuted((value) => !value);
            }}
          >
            {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />} {isMuted ? "Unmute" : "Mute"}
          </Button>
        )}
        <Button variant="outline" onClick={prev} disabled={index === 0}>
          <ChevronLeft className="w-4 h-4" /> Previous
        </Button>
        <Button
          variant={card.saved ? "default" : "outline"}
          onClick={() => {
            updateCard(card.id, { saved: !card.saved });
            toast.success(card.saved ? "Removed from revision" : "Saved to revision");
          }}
        >
          <Bookmark className="w-4 h-4" /> {card.saved ? "Saved" : "Save for Revision"}
        </Button>
        <Button
          variant={card.favorite ? "default" : "outline"}
          onClick={() => {
            updateCard(card.id, { favorite: !card.favorite });
            toast.success(card.favorite ? "Removed from favorites" : "Added to favorites");
          }}
        >
          <Heart className={`w-4 h-4 ${card.favorite ? "fill-current" : ""}`} /> Favorite
        </Button>
        <Button
          variant={card.known ? "default" : "outline"}
          onClick={() => {
            updateCard(card.id, { known: !card.known, notKnownCount: card.known ? card.notKnownCount + 1 : card.notKnownCount });
            toast.success(card.known ? "Marked as not known" : "Marked as known 🎉");
            if (!card.known) next();
          }}
        >
          <CheckCircle2 className="w-4 h-4" /> {card.known ? "Known" : "I Know This"}
        </Button>
        <Button
          variant="outline"
          className="text-destructive hover:text-destructive"
          onClick={() => {
            deleteCard(card.id);
            toast.success("Card deleted");
          }}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
        <Button onClick={next} disabled={index === cards.length - 1}>
          Next <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
