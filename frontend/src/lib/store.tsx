import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { AppState, Flashcard, FlashcardSet, User } from "./types";

const STORAGE_KEY = "smart-flashcard-ai:v1";

const defaultState: AppState = {
  user: null,
  sets: [],
  cards: [],
  theme: "light",
};

interface Ctx {
  state: AppState;
  setUser: (u: User | null) => void;
  addSet: (set: FlashcardSet, cards: Flashcard[]) => void;
  updateCard: (id: string, patch: Partial<Flashcard>) => void;
  deleteCard: (id: string) => void;
  deleteSet: (id: string) => void;
  renameSet: (id: string, title: string) => void;
  duplicateSet: (id: string) => void;
  toggleTheme: () => void;
  setTheme: (t: "light" | "dark") => void;
}

const StoreContext = createContext<Ctx | null>(null);

function loadState(): AppState {
  if (typeof window === "undefined") return defaultState;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState;
    return { ...defaultState, ...JSON.parse(raw) };
  } catch {
    return defaultState;
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>(defaultState);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setState(loadState());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    document.documentElement.classList.toggle("dark", state.theme === "dark");
  }, [state, hydrated]);

  const setUser = useCallback((user: User | null) => {
    setState((s) => ({ ...s, user }));
  }, []);

  const addSet = useCallback((set: FlashcardSet, cards: Flashcard[]) => {
    setState((s) => ({ ...s, sets: [set, ...s.sets], cards: [...cards, ...s.cards] }));
  }, []);

  const updateCard = useCallback((id: string, patch: Partial<Flashcard>) => {
    setState((s) => ({
      ...s,
      cards: s.cards.map((c) => (c.id === id ? { ...c, ...patch } : c)),
    }));
  }, []);

  const deleteCard = useCallback((id: string) => {
    setState((s) => ({
      ...s,
      cards: s.cards.filter((c) => c.id !== id),
      sets: s.sets.map((st) => ({ ...st, flashcardIds: st.flashcardIds.filter((x) => x !== id) })),
    }));
  }, []);

  const deleteSet = useCallback((id: string) => {
    setState((s) => ({
      ...s,
      sets: s.sets.filter((x) => x.id !== id),
      cards: s.cards.filter((c) => c.setId !== id),
    }));
  }, []);

  const renameSet = useCallback((id: string, title: string) => {
    setState((s) => ({ ...s, sets: s.sets.map((x) => (x.id === id ? { ...x, title } : x)) }));
  }, []);

  const duplicateSet = useCallback((id: string) => {
    setState((s) => {
      const orig = s.sets.find((x) => x.id === id);
      if (!orig) return s;
      const newSetId = crypto.randomUUID();
      const newCards = s.cards
        .filter((c) => c.setId === id)
        .map((c) => ({ ...c, id: crypto.randomUUID(), setId: newSetId, known: false, saved: false, favorite: false, notKnownCount: 0 }));
      const newSet: FlashcardSet = {
        ...orig,
        id: newSetId,
        title: orig.title + " (Copy)",
        createdAt: Date.now(),
        flashcardIds: newCards.map((c) => c.id),
      };
      return { ...s, sets: [newSet, ...s.sets], cards: [...newCards, ...s.cards] };
    });
  }, []);

  const setTheme = useCallback((t: "light" | "dark") => {
    setState((s) => ({ ...s, theme: t }));
  }, []);
  const toggleTheme = useCallback(() => {
    setState((s) => ({ ...s, theme: s.theme === "light" ? "dark" : "light" }));
  }, []);

  const value = useMemo<Ctx>(() => ({
    state, setUser, addSet, updateCard, deleteCard, deleteSet,
    renameSet, duplicateSet, toggleTheme, setTheme,
  }), [state, setUser, addSet, updateCard, deleteCard, deleteSet, renameSet, duplicateSet, toggleTheme, setTheme]);

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useStore must be inside StoreProvider");
  return ctx;
}
