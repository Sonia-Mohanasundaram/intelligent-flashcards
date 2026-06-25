export type Difficulty = "Easy" | "Medium" | "Hard";
export type Priority = "Low" | "Medium" | "High";

export interface Flashcard {
  id: string;
  setId: string;
  question: string;
  answer: string;
  difficulty: Difficulty;
  priority: Priority;
  known: boolean;
  saved: boolean;
  favorite: boolean;
  notKnownCount: number;
  createdAt: number;
}

export interface FlashcardSet {
  id: string;
  title: string;
  subject: string;
  topic: string;
  notes: string;
  summary: string[];
  keywords: string[];
  entities: { label: string; type: string }[];
  difficulty: Difficulty;
  totalWords: number;
  createdAt: number;
  flashcardIds: string[];
}

export interface User {
  name: string;
  email: string;
}

export interface AppState {
  user: User | null;
  sets: FlashcardSet[];
  cards: Flashcard[];
  theme: "light" | "dark";
}
