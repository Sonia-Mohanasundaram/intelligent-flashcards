import type { Difficulty, Flashcard, FlashcardSet } from "./types";

const STOPWORDS = new Set([
  "the","a","an","and","or","but","is","are","was","were","be","been","being","of","to","in","on","at",
  "for","with","by","from","as","that","this","these","those","it","its","into","than","then","so","such",
  "can","will","would","should","could","may","might","do","does","did","has","have","had","not","no",
  "if","while","when","where","which","who","whom","what","how","also","very","more","most","some","any",
  "each","other","one","two","three","study","studies","learning","student","students","example","examples",
  "topic","topics","concept","concepts","term","terms","definition","definitions","material","materials","information",
  "important","important","key","keys","notes","note","subject","subjects","content","contents","focus","focused",
]);

const GENERIC_PHRASES = new Set([
  "main idea","core idea","key concept","important concept","general knowledge","subject matter","study notes",
  "theory","system","process","method","example","information","data","result","results"
]);

const CATEGORY_KEYWORDS: Record<string, string[]> = {
  Theory: ["theory", "principle", "law", "model", "framework", "paradigm"],
  Process: ["process", "method", "approach", "procedure", "mechanism", "workflow", "function"],
  System: ["system", "architecture", "structure", "network", "framework"],
  Concept: ["concept", "term", "definition", "idea", "topic", "component"],
};

function normalizeText(input: string) {
  return input.replace(/\s+/g, " ").trim();
}

function splitSentences(text: string) {
  return text
    .replace(/\n+/g, ". ")
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => normalizeText(sentence))
    .filter((sentence) => sentence.length >= 12);
}

function tokenize(text: string) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((token) => token.length > 2 && !STOPWORDS.has(token));
}

function titleCase(phrase: string) {
  return phrase
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function isGenericPhrase(phrase: string) {
  const normalized = phrase.toLowerCase().trim();
  if (GENERIC_PHRASES.has(normalized)) return true;
  return normalized.split(" ").every((token) => STOPWORDS.has(token) || token.length <= 3);
}

function extractCandidates(sentences: string[]) {
  const termMap = new Map<string, { raw: string; count: number; sentenceCount: number; firstIndex: number; words: number }>();

  sentences.forEach((sentence, sentenceIndex) => {
    const tokens = sentence
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter(Boolean);
    const filtered = tokens.filter((token) => token.length > 2 && !STOPWORDS.has(token));

    for (let n = 1; n <= 3; n += 1) {
      for (let i = 0; i + n <= filtered.length; i += 1) {
        const phrase = filtered.slice(i, i + n).join(" ");
        if (phrase.length < 4 || isGenericPhrase(phrase)) continue;

        const raw = titleCase(phrase);
        const existing = termMap.get(phrase);
        if (existing) {
          existing.count += 1;
          if (existing.firstIndex > sentenceIndex) existing.firstIndex = sentenceIndex;
          if (!existing.sentenceCount || existing.firstIndex !== sentenceIndex) existing.sentenceCount += 1;
        } else {
          termMap.set(phrase, {
            raw,
            count: 1,
            sentenceCount: 1,
            firstIndex: sentenceIndex,
            words: n,
          });
        }
      }
    }
  });

  return Array.from(termMap.entries()).map(([phrase, info]) => ({
    phrase,
    raw: info.raw,
    count: info.count,
    sentenceCount: info.sentenceCount,
    firstIndex: info.firstIndex,
    words: info.words,
  }));
}

function rankKeywords(candidates: Array<{ phrase: string; raw: string; count: number; sentenceCount: number; firstIndex: number; words: number }>) {
  const scored = candidates
    .map((candidate) => {
      const positionBonus = 1 + Math.max(0, 12 - candidate.firstIndex) * 0.08;
      const sentenceBonus = 1 + candidate.sentenceCount * 0.25;
      const lengthBonus = candidate.words > 1 ? 1.3 : 1;
      const score = candidate.count * sentenceBonus * positionBonus * lengthBonus;
      return { ...candidate, score };
    })
    .sort((a, b) => b.score - a.score);

  const selected: Array<{ label: string; score: number }> = [];
  for (const candidate of scored) {
    if (selected.length >= 20) break;
    const lower = candidate.phrase;
    if (selected.some((existing) => existing.label.toLowerCase().includes(lower) || lower.includes(existing.label.toLowerCase()))) {
      continue;
    }
    selected.push({ label: candidate.raw, score: candidate.score });
  }

  return selected.slice(0, 12);
}

function selectKeywords(candidates: Array<{ label: string; score: number }>) {
  const keywords = candidates
    .filter((candidate) => candidate.label.length <= 45)
    .slice(0, 10)
    .map((candidate) => candidate.label);
  return Array.from(new Set(keywords));
}

function inferTopic(topics: string[], keywords: string[]) {
  if (topics.length > 0) return topics[0];
  if (keywords.length > 0) return keywords[0];
  return "General Knowledge";
}

function extractEntities(keywords: string[]) {
  const entities: { label: string; type: string }[] = [];
  for (const keyword of keywords.slice(0, 8)) {
    const lower = keyword.toLowerCase();
    let type = "Concept";
    for (const [category, tokens] of Object.entries(CATEGORY_KEYWORDS)) {
      if (tokens.some((token) => lower.includes(token))) {
        type = category;
        break;
      }
    }
    if (!isGenericPhrase(lower)) {
      entities.push({ label: keyword, type });
    }
    if (entities.length >= 6) break;
  }
  return entities;
}

function extractTopics(keywords: string[], entities: { label: string; type: string }[]) {
  const candidates = [...keywords, ...entities.map((entity) => entity.label)];
  const topics: string[] = [];
  for (const candidate of candidates) {
    const lower = candidate.toLowerCase();
    if (topics.some((topic) => topic.toLowerCase() === lower)) continue;
    if (isGenericPhrase(lower)) continue;
    topics.push(candidate);
    if (topics.length >= 8) break;
  }
  return topics;
}

function scoreSentences(sentences: string[], keywords: string[]) {
  const keywordSet = new Set(keywords.map((keyword) => keyword.toLowerCase()));

  return sentences.map((sentence, index) => {
    const normalized = sentence.toLowerCase();
    const tokens = normalized.split(/\s+/).filter(Boolean);
    const presence = keywords.reduce((count, keyword) => (normalized.includes(keyword.toLowerCase()) ? count + 1 : count), 0);
    const lengthScore = Math.max(1, Math.min(3, tokens.length / 15));
    const positionScore = 1.2 - index * 0.08;
    const keywordCoverage = presence > 0 ? 1 + presence * 0.3 : 1;
    const score = keywordCoverage * lengthScore * Math.max(0.5, positionScore);
    return { sentence, score, index, keywordMatches: presence };
  });
}

function cleanSummarySentence(sentence: string) {
  let output = sentence.replace(/\s+/g, " ").trim();
  output = output.replace(/^(This|These)\s+/i, "It ");
  output = output.replace(/\s+\(.*?\)/g, "");
  if (output.endsWith(".")) return output;
  return `${output}.`;
}

function generateSummary(topics: string[], sentences: string[]) {
  const topicPhrase = topics.length ? topics.slice(0, 4).join(", ").replace(/, ([^,]*)$/, " and $1") : "core ideas";
  const shortSentences = sentences.map(cleanSummarySentence).slice(0, 3);
  const summary: string[] = [];

  summary.push(`This text focuses on ${topicPhrase}.`);
  if (shortSentences[0]) {
    summary.push(shortSentences[0]);
  }
  if (shortSentences[1]) {
    summary.push(shortSentences[1]);
  }

  return summary.slice(0, 4);
}

function createQuestion(term: string, sentence: string) {
  const lower = sentence.toLowerCase();
  const normalizedTerm = term.endsWith("s") ? term : term;
  let question = `What is ${normalizedTerm}?`;
  let difficulty: Difficulty = "Medium";

  if (/\bfunction\b|\bpurpose\b|\brole\b/.test(lower)) {
    question = `What is the function of ${term}?`;
    difficulty = "Medium";
  } else if (/\bwhy\b|\bbecause\b|\bdue to\b/.test(lower)) {
    question = `Why is ${term} important?`;
    difficulty = "Hard";
  } else if (/\bcompare\b|\bdifference\b|\bversus\b|\bthan\b/.test(lower)) {
    question = `How does ${term} compare to related concepts?`;
    difficulty = "Hard";
  } else if (/\bdefine\b|\bdefinition\b|\brefers to\b|\bknown as\b/.test(lower) || lower.includes(` ${term.toLowerCase()} is `)) {
    question = `Define ${term}.`;
    difficulty = "Easy";
  } else if (/\bdescribe\b|\bexplain\b|\bdescribe the role\b/.test(lower)) {
    question = `Explain the role of ${term}.`;
    difficulty = "Medium";
  }

  return { question, difficulty };
}

function extractAnswer(term: string, sentence: string) {
  const lowerSentence = sentence.toLowerCase();
  const lowerTerm = term.toLowerCase();
  const defMatch = new RegExp(`(${lowerTerm})\s+(is|are|refers to|means|defines|describes)`, "i");
  const match = sentence.match(defMatch);
  if (match) {
    return sentence.substring(match.index!).trim();
  }
  if (lowerSentence.includes(" because ") || lowerSentence.includes(" due to ")) {
    return sentence.trim();
  }
  return sentence.trim();
}

function buildQuestions(topics: string[], sentences: string[]) {
  const questions: { question: string; answer: string; difficulty: Difficulty }[] = [];
  const seen = new Set<string>();
  const normalizedSentences = sentences.map((sentence) => sentence.replace(/\s+/g, " ").trim());

  for (const topic of topics.slice(0, 8)) {
    const lowerTopic = topic.toLowerCase();
    const match = normalizedSentences.find((sentence) => sentence.toLowerCase().includes(lowerTopic));
    if (!match) continue;

    const { question, difficulty } = createQuestion(topic, match);
    const normalizedQuestion = question.toLowerCase();
    if (seen.has(normalizedQuestion)) continue;

    const answer = extractAnswer(topic, match);
    const trimmedAnswer = answer.endsWith(".") ? answer : `${answer}.`;
    if (trimmedAnswer.length < 10) continue;

    questions.push({ question, answer: trimmedAnswer, difficulty });
    seen.add(normalizedQuestion);
    if (questions.length >= 8) break;
  }

  if (questions.length < 6) {
    for (const sentence of normalizedSentences) {
      if (questions.length >= 6) break;
      const cleaned = cleanSummarySentence(sentence);
      const firstTerm = topics[questions.length] ?? "this concept";
      const question = `What is ${firstTerm}?`;
      if (seen.has(question.toLowerCase())) continue;
      questions.push({ question, answer: cleaned, difficulty: "Medium" });
      seen.add(question.toLowerCase());
    }
  }

  return questions.slice(0, 8);
}

function inferDifficulty(totalWords: number, keywordCount: number, questionCount: number): Difficulty {
  if (totalWords > 420 || keywordCount > 8 || questionCount > 6) return "Hard";
  if (totalWords > 240 || keywordCount > 5) return "Medium";
  return "Easy";
}

export interface AIResult {
  summary: string[];
  keywords: string[];
  entities: { label: string; type: string }[];
  topics: string[];
  questions: { question: string; answer: string; difficulty: Difficulty }[];
  topic: string;
  subject: string;
  difficulty: Difficulty;
  totalWords: number;
}

export function analyzeNotes(notes: string): AIResult {
  const text = normalizeText(notes);
  const sentences = splitSentences(text);
  const tokens = tokenize(text);
  const totalWords = tokens.length;

  const candidates = extractCandidates(sentences);
  const ranked = rankKeywords(candidates);
  const keywords = selectKeywords(ranked);
  const entities = extractEntities(keywords);
  const topics = extractTopics(keywords, entities);
  const importantSentences = scoreSentences(sentences, keywords)
    .sort((a, b) => b.score - a.score)
    .slice(0, 4)
    .map((item) => item.sentence);

  const summary = generateSummary(topics, importantSentences);
  const questions = buildQuestions(topics, importantSentences);
  const difficulty = inferDifficulty(totalWords, keywords.length, questions.length);
  const topic = inferTopic(topics, keywords);

  return {
    summary: summary.length ? summary : ["These notes focus on the most important study concepts."],
    keywords,
    entities,
    topics,
    questions,
    topic,
    subject: topic,
    difficulty,
    totalWords,
  };
}

export function buildSetFromResult(notes: string, result: AIResult): { set: FlashcardSet; cards: Flashcard[] } {
  const setId = crypto.randomUUID();
  const cards: Flashcard[] = result.questions.map((q) => ({
    id: crypto.randomUUID(),
    setId,
    question: q.question,
    answer: q.answer,
    difficulty: q.difficulty,
    priority: q.difficulty === "Hard" ? "High" : q.difficulty === "Medium" ? "Medium" : "Low",
    known: false,
    saved: false,
    favorite: false,
    notKnownCount: 0,
    createdAt: Date.now(),
  }));

  const set: FlashcardSet = {
    id: setId,
    title: `${result.topic || result.subject} — ${new Date().toLocaleDateString()}`,
    topic: result.topic || result.subject,
    subject: result.subject,
    notes,
    summary: result.summary,
    keywords: result.keywords,
    entities: result.entities,
    difficulty: result.difficulty,
    totalWords: result.totalWords,
    createdAt: Date.now(),
    flashcardIds: cards.map((c) => c.id),
  };

  return { set, cards };
}
