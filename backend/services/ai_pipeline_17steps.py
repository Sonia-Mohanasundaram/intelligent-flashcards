"""
Local AI processing pipeline for Smart Flashcard AI.

Uses spaCy en_core_web_sm for linguistic analysis and local Hugging Face
t5-small weights for summarization and question wording. No external AI APIs.
"""

import logging
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

logger = logging.getLogger(__name__)

GENERIC_KEYWORDS = {
    'place', 'first', 'second', 'third', 'end', 'that', 'this', 'these', 'those',
    'take', 'follow', 'thing', 'example', 'case', 'point', 'process', 'method', 'way',
    'part', 'type', 'system', 'data', 'information', 'result', 'object', 'use', 'value',
    'form', 'step', 'time', 'model', 'structure', 'element', 'elements', 'task', 'tasks',
    'order', 'behavior', 'computing', 'technology', 'application', 'applications',
    'development', 'software', 'hardware', 'research', 'analysis', 'study', 'topic',
    'topics', 'concept', 'concepts', 'entity', 'entities', 'detail', 'details', 'item',
    'items', 'area', 'areas', 'field', 'fields', 'environment', 'resource', 'resources',
    'machine', 'machines', 'decision', 'decisions', 'error', 'errors', 'weight', 'weights',
    'training', 'learning', 'knowledge', 'information', 'sentence', 'sentences'
}

PIPELINE_TIMELINE = [
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
]


class AIProcessingPipeline:
    """Complete local-only AI pipeline for notes-to-flashcards processing."""

    _nlp = None
    _t5_tokenizer = None
    _t5_model = None
    _device = None

    def __init__(self):
        self.nlp = self._load_spacy()
        self.t5_tokenizer, self.t5_model, self.device = self._load_t5()

    @classmethod
    def _load_spacy(cls):
        if cls._nlp is None:
            try:
                cls._nlp = spacy.load("en_core_web_sm")
            except OSError as exc:
                raise RuntimeError(
                    "spaCy model en_core_web_sm is not installed. Install requirements.txt first."
                ) from exc
        return cls._nlp

    @classmethod
    def _load_t5(cls):
        if cls._t5_model is None or cls._t5_tokenizer is None:
            try:
                cls._t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
                cls._t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
                cls._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                cls._t5_model.to(cls._device)
                cls._t5_model.eval()
            except Exception as exc:
                logger.warning("t5-small unavailable; using extractive local fallbacks: %s", exc)
                cls._t5_tokenizer = None
                cls._t5_model = None
                cls._device = torch.device("cpu")
        return cls._t5_tokenizer, cls._t5_model, cls._device

    def process(self, text: str, title: str = "Untitled") -> Dict:
        started_at = datetime.utcnow()

        try:
            raw_text = text or ""
            cleaned_text = self._clean_text(raw_text)
            if len(cleaned_text) < 40:
                raise ValueError("Please provide at least 40 characters of notes.")

            doc = self.nlp(cleaned_text)
            tokens = self._content_tokens(doc)
            filtered_text = " ".join(token.lemma_.lower() for token in tokens)
            sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) >= 4]
            keywords = self._extract_keywords(doc)
            entities = self._extract_entities(doc)
            ranked_sentences = self._rank_sentences(sentences, keywords, entities)
            topic = self._extract_primary_topic(keywords, entities, ranked_sentences, doc)
            topics = self._extract_topics(keywords, doc)
            summary = self._generate_summary(ranked_sentences, cleaned_text)
            question_specs = self._generate_questions(ranked_sentences, keywords, topics, topic, entities)
            flashcards = self._generate_answers(question_specs, ranked_sentences, keywords, entities)
            flashcards = self._classify_flashcards(flashcards, doc)
            display_entities = entities if entities else [
                {"label": "No named entities detected", "text": "", "type": "Info", "entityType": "NONE"}
            ]
            flashcards = self._score_confidence(flashcards, keywords, entities)

            word_count = len([token for token in doc if not token.is_space and not token.is_punct])
            study_minutes = self._estimate_study_time(len(flashcards))
            result = {
                "success": True,
                "title": title,
                "topic": topic,
                "subject": topic,
                "confidence": self._average_confidence(flashcards),
                "difficulty": self._average_difficulty(flashcards),
                "readingLevel": self._reading_level(doc, word_count),
                "studyTime": f"{study_minutes} min",
                "readingTime": self._estimate_reading_time(word_count),
                "wordCount": word_count,
                "characterCount": len(cleaned_text),
                "questionCount": len(flashcards),
                "keywords": keywords,
                "entities": display_entities,
                "topics": topics,
                "flashcards": flashcards,
                "cleanedText": cleaned_text,
                "filteredText": filtered_text,
                "pipeline": self._pipeline_steps(),
                "pipelineTimeline": PIPELINE_TIMELINE,
                "insights": {},
                "processedAt": started_at.isoformat(),
            }
            result["insights"] = self._insights(result)
            return result
        except Exception as exc:
            logger.error("AI pipeline failed: %s", exc, exc_info=True)
            return {"success": False, "error": str(exc), "pipeline": self._pipeline_steps("failed")}

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text.replace("\x00", " "))
        text = re.sub(r"([.!?])([A-Z])", r"\1 \2", text)
        return text.strip()

    def _content_tokens(self, doc) -> List:
        return [
            token for token in doc
            if not token.is_stop
            and not token.is_punct
            and not token.is_space
            and not token.like_num
            and len(token.text.strip()) > 2
            and token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"}
        ]

    def _extract_keywords(self, doc) -> List[str]:
        scores = defaultdict(float)

        for chunk in doc.noun_chunks:
            normalized = self._normalize_phrase(chunk.text)
            if not normalized or self._is_generic_term(normalized):
                continue
            filtered_tokens = [token for token in chunk if not token.is_stop and token.pos_ not in {"DET", "PRON", "PART", "PUNCT"}]
            phrase = self._normalize_phrase(" ".join(token.text for token in filtered_tokens))
            if not phrase or self._is_generic_term(phrase) or len(phrase.split()) > 5:
                continue
            if len(phrase.split()) == 1 and chunk.root.pos_ not in {"NOUN", "PROPN"}:
                continue
            scores[phrase] += 5.0 + min(len(phrase.split()), 4)

        for ent in doc.ents:
            normalized = self._normalize_phrase(ent.text)
            if normalized and not self._is_generic_term(normalized):
                scores[normalized] += 6.0

        if not scores:
            for token in self._content_tokens(doc):
                lemma = token.lemma_.lower()
                if not lemma or self._is_generic_term(lemma):
                    continue
                if token.pos_ not in {"NOUN", "PROPN"}:
                    continue
                scores[lemma] += 2.0

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        selected = []
        for phrase, _ in ranked:
            title_phrase = phrase.title()
            if title_phrase not in selected and len(selected) < 10:
                selected.append(title_phrase)
        return selected

    def _extract_entities(self, doc) -> List[Dict]:
        label_names = {
            "PERSON": "Person",
            "ORG": "Organization",
            "GPE": "Location",
            "LOC": "Location",
            "PRODUCT": "Product",
            "EVENT": "Event",
            "DATE": "Date",
            "TIME": "Time",
            "WORK_OF_ART": "Work",
            "LAW": "Law",
            "LANGUAGE": "Language",
            "NORP": "Group",
            "FAC": "Facility",
        }
        entities = []
        seen = set()
        for ent in doc.ents:
            text = ent.text.strip()
            key = (text.lower(), ent.label_)
            if ent.label_ in label_names and key not in seen:
                seen.add(key)
                entities.append({"label": text, "text": text, "type": label_names[ent.label_], "entityType": ent.label_})
        return entities[:20]

    def _rank_sentences(self, sentences: List[str], keywords: List[str], entities: List[Dict]) -> List[Dict]:
        keyword_terms = [keyword.lower() for keyword in keywords]
        entity_terms = [entity["label"].lower() for entity in entities]
        ranked = []

        for index, sentence in enumerate(sentences):
            lower_sentence = sentence.lower()
            keyword_hits = sum(1 for keyword in keyword_terms if keyword in lower_sentence)
            entity_hits = sum(1 for entity in entity_terms if entity in lower_sentence)
            length = len(sentence.split())
            length_score = 1.3 if 10 <= length <= 45 else 0.5
            density = min(keyword_hits + entity_hits, 4)
            score = density * 2.5 + length_score + max(0, 1.0 - index * 0.03)
            ranked.append({"text": sentence, "score": round(score, 3), "index": index})

        return sorted(ranked, key=lambda item: item["score"], reverse=True)

    def _generate_summary(self, ranked_sentences: List[Dict], cleaned_text: str) -> List[str]:
        source = " ".join(item["text"] for item in ranked_sentences[:6]) or cleaned_text
        generated = self._t5_generate(
            f"summarize: {source}",
            max_length=120,
            min_length=40,
            num_beams=4,
        )
        candidates = self._split_summary(generated) if generated else []
        if len(candidates) < 3:
            candidates = [item["text"] for item in ranked_sentences[:4]]
        return [self._ensure_period(item) for item in candidates[:4] if len(item.split()) >= 5][:4]

    def _generate_questions(
        self,
        ranked_sentences: List[Dict],
        keywords: List[str],
        topics: List[str],
        topic: str,
        entities: List[Dict],
    ) -> List[Dict]:
        concepts = self._question_concepts(keywords, topics, ranked_sentences, entities)
        if not concepts:
            concepts = [topic]

        specs = []
        seen_questions = set()
        seen_concept_types = set()
        last_concept = None

        for sentence in ranked_sentences:
            sentence_text = sentence["text"]
            list_items = self._detect_list_items(sentence_text)
            concept = self._resolve_sentence_concept(sentence_text, concepts, last_concept)
            if not concept:
                continue
            
            q_type = self._infer_question_type(sentence_text, concept, list_items)
            concept_type_key = (concept.lower(), q_type)
            
            if concept_type_key in seen_concept_types and not list_items:
                continue
            last_concept = concept

            related = self._find_related_concept_in_sentence(sentence_text, concept, concepts)
            prompt = self._question_prompt(q_type, concept, related, sentence_text, list_items)
            generated = self._t5_generate(prompt, max_length=64, min_length=14, num_beams=4)
            question = self._clean_question(generated, "", concept)

            if not question or self._is_poor_question(question, concept):
                question = self._fallback_question(q_type, concept, related, topic, list_items)

            if not self._is_valid_concept(concept):
                continue

            key = (question.lower(), concept.lower())
            if key not in seen_questions:
                seen_questions.add(key)
                seen_concept_types.add(concept_type_key)
                specs.append({
                    "question": question,
                    "type": q_type,
                    "keyword": concept,
                    "related": related,
                    "source": sentence,
                })
            if len(specs) >= 5:
                break

        return specs

    def _generate_answers(
        self,
        question_specs: List[Dict],
        ranked_sentences: List[Dict],
        keywords: List[str],
        entities: List[Dict],
    ) -> List[Dict]:
        flashcards = []
        for spec in question_specs:
            answer_sentences = self._answer_sentences(spec, ranked_sentences)
            if not answer_sentences:
                continue
            answer = self._normalize_answer(" ".join(self._ensure_period(sentence["text"]) for sentence in answer_sentences))
            if len(answer.split()) < 5:
                continue
            flashcards.append({
                "question": spec["question"],
                "answer": answer,
                "difficulty": "Medium",
                "confidence": 0,
                "topic": spec["keyword"],
                "type": spec["type"],
                "keyword": spec["keyword"],
                "sourceSentence": spec["source"]["text"],
                "sentenceImportance": spec["source"]["score"],
                "keywordRelevance": self._term_relevance(answer, keywords),
                "entityRelevance": self._entity_relevance(answer, entities),
                "known": False,
                "favorite": False,
                "revisionStatus": "new",
                "revisionPriority": "medium",
                "created": datetime.utcnow().isoformat(),
            })
        return flashcards

    def _classify_flashcards(self, flashcards: List[Dict], doc) -> List[Dict]:
        entity_count = len(list(doc.ents))
        for card in flashcards:
            answer_words = len(card["answer"].split())
            score = 0
            score += {"definition": 1, "why": 2, "how": 2, "comparison": 3, "application": 3}.get(card["type"], 2)
            score += 1 if answer_words < 18 else 2 if answer_words < 40 else 3
            score += 1 if card["keywordRelevance"] < 0.25 else 2
            score += 1 if entity_count >= 4 else 0
            if score <= 4:
                card["difficulty"] = "Easy"
                card["revisionPriority"] = "low"
            elif score <= 7:
                card["difficulty"] = "Medium"
                card["revisionPriority"] = "medium"
            else:
                card["difficulty"] = "Hard"
                card["revisionPriority"] = "high"
        return flashcards

    def _score_confidence(self, flashcards: List[Dict], keywords: List[str], entities: List[Dict]) -> List[Dict]:
        max_importance = max((card["sentenceImportance"] for card in flashcards), default=1.0) or 1.0
        for card in flashcards:
            keyword_score = card["keywordRelevance"] * 35
            entity_score = card["entityRelevance"] * 20
            sentence_score = min(1.0, card["sentenceImportance"] / max_importance) * 35
            answer_score = min(1.0, len(card["answer"].split()) / 24) * 10
            card["confidence"] = max(50, min(98, round(keyword_score + entity_score + sentence_score + answer_score)))
        return flashcards

    def _extract_primary_topic(self, keywords: List[str], entities: List[Dict], ranked_sentences: List[Dict], doc) -> str:
        candidates = []
        seen = set()
        entity_labels = {entity["label"] for entity in entities}

        for entity in entities:
            normalized = self._normalize_phrase(entity["label"])
            if normalized and self._is_valid_concept(normalized) and normalized not in seen:
                seen.add(normalized)
                candidates.append((normalized, 10.0, True))

        top_sentence_text = " ".join(item["text"] for item in ranked_sentences[:6])
        top_doc = self.nlp(top_sentence_text)
        for chunk in top_doc.noun_chunks:
            normalized = self._normalize_phrase(chunk.text)
            if not normalized or normalized in seen or self._is_generic_term(normalized):
                continue
            if len(normalized.split()) > 5:
                continue
            if not self._is_valid_concept(normalized):
                continue
            seen.add(normalized)
            is_entity = normalized.title() in entity_labels
            candidates.append((normalized, 6.0 if is_entity else 4.0, is_entity))

        for keyword in keywords[:10]:
            normalized = self._normalize_phrase(keyword)
            if not normalized or normalized in seen or self._is_generic_term(normalized):
                continue
            if not self._is_valid_concept(normalized):
                continue
            seen.add(normalized)
            candidates.append((normalized, 3.0, False))

        if not candidates:
            return "General Knowledge"

        scores = {}
        text_lower = top_sentence_text.lower()
        for normalized, base, is_entity in candidates:
            words = normalized.split()
            frequency = sum(1 for match in re.finditer(r"\b" + re.escape(words[-1]) + r"\b", text_lower))
            sentence_score = sum(item["score"] for item in ranked_sentences if normalized in item["text"].lower())
            length_bonus = min(3, len(words)) * 1.2
            proper_noun_bonus = 2.0 if is_entity or self._is_proper_noun_phrase(normalized, doc) else 0.0
            phrase_is_single = len(words) == 1
            penalty = 0.0 if not phrase_is_single else 1.0
            total = base + frequency * 1.5 + sentence_score * 1.2 + length_bonus + proper_noun_bonus - penalty
            scores[normalized] = max(scores.get(normalized, 0.0), total)

        best = max(scores.items(), key=lambda item: (item[1], len(item[0].split()), item[0]))[0]
        return best.title()

    def _is_proper_noun_phrase(self, phrase: str, doc) -> bool:
        for chunk in doc.noun_chunks:
            normalized = self._normalize_phrase(chunk.text)
            if normalized == phrase:
                return all(token.pos_ == "PROPN" for token in chunk if not token.is_stop)
        return False

    def _extract_topics(self, keywords: List[str], doc) -> List[str]:
        topics = []
        for ent in doc.ents:
            normalized = self._normalize_phrase(ent.text)
            if normalized and self._is_valid_concept(normalized) and normalized.title() not in topics:
                topics.append(normalized.title())
            if len(topics) >= 10:
                break

        for keyword in keywords:
            normalized = self._normalize_phrase(keyword)
            if not normalized or normalized.title() in topics:
                continue
            if not self._is_valid_concept(normalized):
                continue
            if len(normalized.split()) == 1 and normalized.lower() in GENERIC_KEYWORDS:
                continue
            topics.append(normalized.title())
            if len(topics) >= 10:
                break
        return topics[:10]

    def _question_concepts(
        self,
        keywords: List[str],
        topics: List[str],
        ranked_sentences: List[Dict],
        entities: List[Dict],
    ) -> List[str]:
        sentence_concepts = self._extract_sentence_concepts(ranked_sentences, entities)
        candidates = [*sentence_concepts]
        if len(candidates) < 3:
            candidates.extend(topics)
        if len(candidates) < 5:
            candidates.extend(keywords)

        concepts = []
        seen = set()
        for item in candidates:
            if not item:
                continue
            normalized = self._normalize_phrase(item)
            if not normalized or normalized in seen or self._is_generic_term(normalized):
                continue
            if not self._is_valid_concept(normalized):
                continue
            seen.add(normalized)
            concepts.append(item.title())
            if len(concepts) >= 5:
                break
        return self._merge_similar_concepts(concepts)[:5]

    def _extract_sentence_concepts(self, ranked_sentences: List[Dict], entities: List[Dict]) -> List[str]:
        seen = set()
        concepts = []
        entity_text = {entity["label"].lower() for entity in entities}
        definition_pattern = re.compile(
            r"\b([A-Z][A-Za-z0-9+#\-\s]{2,}?)\s+is\s+(?:a|an|the)\s+([A-Za-z0-9+#\-\s]{3,}?)(?:[\.,;]|\s|$)",
            re.I,
        )

        for sentence in ranked_sentences[:8]:
            text = sentence["text"].strip()
            for match in definition_pattern.finditer(text):
                for candidate in [match.group(1), match.group(2)]:
                    normalized = self._normalize_phrase(candidate)
                    if self._is_valid_concept(normalized):
                        title_phrase = normalized.title()
                        if title_phrase not in seen:
                            seen.add(title_phrase)
                            concepts.append(title_phrase)
                            if len(concepts) >= 6:
                                return concepts

            doc = self.nlp(text)
            for chunk in doc.noun_chunks:
                normalized = self._normalize_phrase(chunk.text)
                if not normalized or normalized in seen:
                    continue
                if self._is_generic_term(normalized):
                    continue
                if chunk.root.pos_ not in {"NOUN", "PROPN", "ADJ"}:
                    continue
                if any(token.pos_ == "PRON" for token in chunk):
                    continue
                if len(normalized.split()) > 4:
                    continue
                if sum(1 for token in doc if token.text.lower() == normalized) > 2:
                    continue
                if any(word in GENERIC_KEYWORDS for word in normalized.split()):
                    continue
                if normalized in entity_text or self._is_valid_concept(normalized):
                    title_phrase = normalized.title()
                    if title_phrase not in seen:
                        seen.add(title_phrase)
                        concepts.append(title_phrase)
                        if len(concepts) >= 6:
                            return concepts
        return self._merge_similar_concepts(concepts)

    def _is_generic_term(self, term: str) -> bool:
        normalized = self._normalize_phrase(term)
        if not normalized:
            return True
        words = normalized.split()
        if normalized in GENERIC_KEYWORDS:
            return True
        if any(word in GENERIC_KEYWORDS or word in STOP_WORDS for word in words):
            return True
        if len(words) == 1 and len(words[0]) <= 3:
            return True
        return False

    def _is_valid_concept(self, term: str) -> bool:
        normalized = self._normalize_phrase(term)
        if not normalized:
            return False
        if self._is_generic_term(normalized):
            return False
        words = normalized.split()
        if len(words) > 5:
            return False
        doc = self.nlp(normalized)
        if not any(token.pos_ in {"NOUN", "PROPN", "ADJ"} and token.text.lower() not in STOP_WORDS for token in doc):
            return False
        if all(token.is_stop or token.pos_ in {"DET", "PRON", "PART", "PUNCT", "CCONJ", "SCONJ"} for token in doc):
            return False
        return True

    def _merge_similar_concepts(self, concepts: List[str]) -> List[str]:
        merged = []
        for concept in sorted(concepts, key=lambda item: (-len(item.split()), item.lower())):
            normalized = self._normalize_phrase(concept)
            if not normalized:
                continue
            if any(
                normalized == self._normalize_phrase(existing)
                or normalized in self._normalize_phrase(existing)
                or self._normalize_phrase(existing) in normalized
                for existing in merged
            ):
                continue
            merged.append(concept)
        return merged

    def _best_source_for_concept(self, concept: str, ranked_sentences: List[Dict]) -> Optional[Dict]:
        concept_lower = concept.lower()
        for sentence in ranked_sentences:
            if concept_lower in sentence["text"].lower():
                return sentence
        return ranked_sentences[0] if ranked_sentences else None

    def _find_concept_for_sentence(self, sentence: str, concepts: List[str]) -> Optional[str]:
        normalized_sentence = self._normalize_phrase(sentence)
        sentence_terms = set(normalized_sentence.split())
        doc = self.nlp(sentence)
        sentence_lemmas = {token.lemma_ for token in doc if not token.is_stop and token.is_alpha}
        
        first_word = sentence.strip().split()[0].lower() if sentence.strip() else ""
        is_strict_pronoun = first_word in {"it", "they", "these", "those", "this", "that"}
        
        for concept in sorted(concepts, key=lambda c: -len(self._normalize_phrase(c))):
            normalized_concept = self._normalize_phrase(concept)
            if not normalized_concept:
                continue
            concept_terms = [term for term in normalized_concept.split() if term not in STOP_WORDS]
            if not concept_terms:
                continue
            
            if len(concept_terms) > 1:
                if all(term in sentence_terms for term in concept_terms):
                    return concept
            elif is_strict_pronoun:
                continue
            elif concept_terms[0] in sentence_terms or concept_terms[0] in sentence_lemmas:
                return concept
        
        for concept in concepts:
            normalized_concept = self._normalize_phrase(concept)
            if not normalized_concept:
                continue
            if is_strict_pronoun:
                break
            concept_lemma = self.nlp(normalized_concept)[0].lemma_ if self.nlp(normalized_concept) else normalized_concept
            if any(term in sentence_terms or term in sentence_lemmas for term in normalized_concept.split() if term not in STOP_WORDS):
                return concept
        return None

    def _find_related_concept_in_sentence(self, sentence: str, concept: str, concepts: List[str]) -> str:
        normalized_sentence = self._normalize_phrase(sentence)
        sentence_terms = set(normalized_sentence.split())
        for candidate in concepts:
            if candidate.lower() == concept.lower():
                continue
            normalized_candidate = self._normalize_phrase(candidate)
            if not normalized_candidate:
                continue
            candidate_terms = [term for term in normalized_candidate.split() if term not in STOP_WORDS]
            if candidate_terms and any(term in sentence_terms for term in candidate_terms):
                return candidate
        return self._related_concept(concept, concepts)

    def _resolve_sentence_concept(self, sentence: str, concepts: List[str], last_concept: Optional[str]) -> Optional[str]:
        normalized_sent = self._normalize_phrase(sentence)
        sent_terms = set(normalized_sent.split()) if normalized_sent else set()
        
        concept = self._find_concept_for_sentence(sentence, concepts)
        if concept:
            return concept
        
        sentence_lower = sentence.lower()
        first_word = sentence.strip().split()[0].lower() if sentence.strip() else ""
        if first_word in {"it", "they", "these", "those", "this", "that"}:
            if last_concept:
                return last_concept
        
        return None

    def _is_pronoun_sentence(self, sentence: str) -> bool:
        first = sentence.strip().split()[0].lower() if sentence.strip() else ""
        return first in {"it", "they", "these", "those", "this", "that"}

    def _answer_sentences(self, spec: Dict, ranked_sentences: List[Dict]) -> List[Dict]:
        concept = spec["keyword"].lower()
        answer_sentences = [spec["source"]]
        if spec["type"] in {"compare", "advantages", "applications", "why", "how", "process"}:
            for sentence in ranked_sentences:
                if sentence["text"] == spec["source"]["text"]:
                    continue
                text_lower = sentence["text"].lower()
                if spec["type"] == "compare" and spec.get("related", ""):
                    if concept in text_lower and spec["related"].lower() in text_lower:
                        answer_sentences = [sentence]
                        break
                elif spec["type"] in {"advantages", "applications", "why", "how", "process"}:
                    if concept in text_lower or spec.get("related", "").lower() in text_lower:
                        answer_sentences.append(sentence)
                if len(answer_sentences) == 2:
                    break
        return answer_sentences[:2]

    def _fallback_question(self, question_type: str, concept: str, related: str, topic: str, list_items: List[str] = None) -> str:
        plural = self._is_plural_term(concept)
        if question_type == "definition":
            article = self._indefinite_article(concept)
            return f"What is {article}{concept}?"
        if question_type == "concept":
            return f"Explain what {concept} is."
        if question_type == "why":
            return f"Why {'are' if plural else 'is'} {concept} important?"
        if question_type == "how":
            return f"How {'do' if plural else 'does'} {concept} work?"
        if question_type == "compare" and related:
            return f"What is the difference between {concept} and {related}?"
        if question_type == "applications":
            return f"What are the applications of {concept}?"
        if question_type == "advantages":
            return f"What are the advantages of {concept}?"
        if question_type == "disadvantages":
            return f"What are the disadvantages of {concept}?"
        if question_type == "where":
            return f"Where is {concept} used?"
        if question_type == "process":
            return f"Explain the working of {concept}."
        if question_type == "list" and list_items:
            return f"What are the key characteristics or types of {concept}?"
        return f"What is {concept}?"

    def _question_prompt(self, question_type: str, concept: str, related: str, source: str, list_items: List[str] = None) -> str:
        if question_type == "definition":
            return (
                f"Write one clear university-level definition question for '{concept}'. "
                f"Start with: 'What is', 'Define', or 'What type of'. End with a question mark. "
                f"Example: 'What is a Queue?' or 'Define polymorphism.' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "concept":
            return (
                f"Write one clear university-level concept question asking to explain '{concept}'. "
                f"Start with: 'Explain', 'Describe', or 'What does'. End with a question mark. "
                f"Example: 'Explain inheritance.' or 'Describe how arrays work.' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "why":
            return (
                f"Write one clear university-level 'why' question about '{concept}'. "
                f"Start with 'Why' and end with a question mark. "
                f"Example: 'Why is encapsulation important in OOP?' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "how":
            return (
                f"Write one clear university-level 'how' question about '{concept}'. "
                f"Start with 'How' and end with a question mark. "
                f"Example: 'How does a Queue manage FIFO ordering?' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "compare":
            if related:
                return (
                    f"Write one clear university-level comparison question between '{concept}' and '{related}'. "
                    f"Start with 'What is the difference' or 'Compare'. End with a question mark. "
                    f"Example: 'What is the difference between Stack and Queue?' "
                    f"Based on: {source}. Output only the question."
                )
            return (
                f"Write one clear university-level comparison question about '{concept}'. "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "applications":
            return (
                f"Write one clear university-level question asking about applications or uses of '{concept}'. "
                f"Start with 'What are the applications', 'Where is', or 'What is used for'. End with a question mark. "
                f"Example: 'What are the applications of binary search?' or 'Where is polymorphism used?' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "advantages":
            return (
                f"Write one clear university-level question asking about advantages of '{concept}'. "
                f"Start with 'What are the advantages' and end with a question mark. "
                f"Example: 'What are the advantages of using inheritance?' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "disadvantages":
            return (
                f"Write one clear university-level question asking about disadvantages of '{concept}'. "
                f"Start with 'What are the disadvantages' and end with a question mark. "
                f"Example: 'What are the disadvantages of global variables?' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "where":
            return (
                f"Write one clear university-level question asking where '{concept}' is used. "
                f"Start with 'Where' and end with a question mark. "
                f"Example: 'Where is recursion used in algorithms?' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "process":
            return (
                f"Write one clear university-level question asking about how '{concept}' works or its steps. "
                f"Start with 'Explain', 'Describe', or 'How'. End with a question mark. "
                f"Example: 'Explain the quicksort algorithm.' or 'Describe the steps involved in compilation.' "
                f"Based on: {source}. Output only the question."
            )
        if question_type == "list" and list_items:
            return (
                f"Write one clear university-level question asking about key features, types, or components of '{concept}'. "
                f"Start with 'What are the' or 'List the'. End with a question mark. "
                f"Example: 'What are the characteristics of a Queue?' or 'List the pillars of OOP.' "
                f"Based on: {source}. Output only the question."
            )
        return (
            f"Write one clear university-level question about '{concept}'. "
            f"Based on: {source}. Output only the question."
        )


    def _clean_question(self, generated: str, fallback: str, concept: str) -> str:
        if not generated:
            return fallback
        candidate = generated.strip()
        candidate = re.sub(r"^(question\s*:\s*)", "", candidate, flags=re.I).strip()
        candidate = re.sub(r"^\(*\s*not[_\s-]*duplicate\)?[\.:\-]*\s*", "", candidate, flags=re.I)
        candidate = re.sub(r"\s{2,}", " ", candidate)
        questions = re.findall(r"([A-Z][^?]*\?)", candidate)
        question = questions[0].strip() if questions else candidate
        question = question.strip()
        if not question.endswith("?"):
            question = question.rstrip(". ") + "?"
        if len(question.split()) < 6 or len(question) > 160 or self._is_poor_question(question, concept) or not self._is_question_text(question):
            return fallback
        return question[0].upper() + question[1:]

    def _is_question_text(self, text: str) -> bool:
        lower = text.lower()
        return bool(re.match(r"^(what|why|how|where|when|which|who|explain|compare|describe|define|list)\b", lower))

    def _is_poor_question(self, question: str, concept: str) -> bool:
        lower = question.lower()
        if lower.startswith("where is") and concept.lower() in lower and len(question.split()) <= 5:
            return True
        if any(term in lower for term in ["place", "thing", "object", "some", "something", "first", "second", "end", "order", "data", "computing"]):
            return True
        if lower.startswith("what are") and len(question.split()) <= 6:
            return True
        if any(pronoun in lower for pronoun in [" what is they", " what are they", " what is it", " what are it", " they are", " it is", " their role"]):
            return True
        if concept.lower() not in lower and not any(word in lower for word in ["why", "how", "compare", "explain", "what does", "what is", "define"]):
            return True
        return False

    def _infer_question_type(self, sentence: str, concept: str, list_items: List[str] = None) -> str:
        text = sentence.lower()
        if list_items:
            return "list"
        if any(keyword in text for keyword in [" vs ", " versus ", " compared to ", " unlike ", " difference between ", " differs from "]):
            return "compare"
        if any(word in text for word in ["because", "therefore", "so that", "in order to", "due to", "since", "as a result"]):
            return "why"
        if any(word in text for word in ["advantage", "benefit", "benefits", "benefit from", "strength"]):
            return "advantages"
        if any(word in text for word in ["disadvantage", "drawback", "limitation", "limitation", "weakness", "limitation"]):
            return "disadvantages"
        if any(word in text for word in ["process", "steps involved", "working of", "how it works", "how the", "works by", "operates by"]):
            return "process"
        if any(word in text for word in ["used for", "use for", "application", "applications", "purpose", "purposes", "used in", "used to"]):
            return "applications"
        if any(word in text for word in ["means", "refers to", "is called", "is defined as", "is a", "is an", "is the"]):
            return "definition"
        if self._is_definition_sentence(sentence, concept):
            return "definition"
        return "concept"

    def _detect_list_items(self, sentence: str) -> List[str]:
        text = sentence.strip()
        if "," not in text:
            return []
        if re.search(r"\b(used|use|application|applications|purpose|for)\b", text.lower()):
            return []
        if not re.search(r"\b(are|is|include|includes|including|consists of|such as|supports|provide|comprises|contains)\b", text.lower()):
            return []
        items = [item.strip() for item in re.split(r",| and | or ", text) if item.strip()]
        if len(items) < 3:
            return []
        filtered = [item for item in items if len(item.split()) <= 6]
        return filtered if len(filtered) >= 3 else []

    def _is_definition_sentence(self, sentence: str, concept: str) -> bool:
        normalized_concept = self._normalize_phrase(concept)
        text = sentence.lower()
        if not normalized_concept:
            return False
        pattern = rf"\b{re.escape(normalized_concept.lower())}\b.*\b(is|are|refers to|means|is called|is defined as)\b"
        return bool(re.search(pattern, text))

    def _t5_generate(self, prompt: str, max_length: int, min_length: int, num_beams: int) -> str:
        if not self.t5_model or not self.t5_tokenizer:
            return ""
        try:
            input_ids = self.t5_tokenizer.encode(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
            ).to(self.device)
            with torch.no_grad():
                output_ids = self.t5_model.generate(
                    input_ids,
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=num_beams,
                    no_repeat_ngram_size=2,
                    early_stopping=True,
                )
            return self.t5_tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
        except Exception as exc:
            logger.warning("T5 generation failed: %s", exc)
            return ""

    def _split_summary(self, summary: str) -> List[str]:
        parts = [part.strip(" -•") for part in re.split(r"(?<=[.!?])\s+|;", summary) if len(part.strip()) > 12]
        return parts

    def _normalize_phrase(self, phrase: str) -> str:
        phrase = re.sub(r"[^A-Za-z0-9+#.\s-]", "", phrase).strip().lower()
        phrase = re.sub(r"\s+", " ", phrase)
        phrase = re.sub(r"^(a|an|the)\s+", "", phrase)
        phrase = re.sub(r"\s+(a|an|the)$", "", phrase)
        if len(phrase) < 3:
            return ""
        if phrase in {"i", "you", "he", "she", "it", "we", "they", "them", "this", "these", "those", "that", "his", "her", "our", "their"}:
            return ""
        return phrase

    def _is_plural_term(self, term: str) -> bool:
        normalized = self._normalize_phrase(term)
        if not normalized:
            return False
        words = normalized.split()
        last = words[-1]
        return last.endswith("s") and not last.endswith("ss")

    def _indefinite_article(self, phrase: str) -> str:
        normalized = self._normalize_phrase(phrase)
        if not normalized:
            return ""
        if normalized.startswith("a ") or normalized.startswith("an ") or normalized.startswith("the "):
            return ""
        if normalized[0] in "aeiou":
            return "an "
        return "a "

    def _related_concept(self, concept: str, concepts: List[str]) -> str:
        for candidate in concepts:
            if candidate.lower() != concept.lower():
                return candidate
        return "another key concept"

    def _term_relevance(self, text: str, keywords: List[str]) -> float:
        if not keywords:
            return 0.0
        lower = text.lower()
        hits = sum(1 for keyword in keywords if keyword.lower() in lower)
        return min(1.0, hits / max(3, min(len(keywords), 8)))

    def _entity_relevance(self, text: str, entities: List[Dict]) -> float:
        if not entities:
            return 0.0
        lower = text.lower()
        hits = sum(1 for entity in entities if entity["label"].lower() in lower)
        return min(1.0, hits / max(1, min(len(entities), 5)))

    def _ensure_period(self, text: str) -> str:
        text = text.strip()
        return text if text.endswith((".", "!", "?")) else f"{text}."

    def _normalize_answer(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return text
        if text.count(".") > 1:
            text = text.split(".", 1)[0].strip() + "."
        text = self._ensure_period(text)
        if text.endswith("??"):
            text = text[:-1]
        return text

    def _reading_level(self, doc, word_count: int) -> str:
        sentences = max(1, len(list(doc.sents)))
        avg_sentence_length = word_count / sentences
        complex_words = sum(1 for token in doc if len(token.text) > 8 and token.is_alpha)
        complexity = avg_sentence_length + (complex_words / max(1, word_count)) * 100
        if complexity < 18:
            return "Middle School"
        if complexity < 28:
            return "High School"
        return "College"

    def _estimate_reading_time(self, word_count: int) -> int:
        return max(1, math.ceil(word_count / 200))

    def _estimate_study_time(self, flashcard_count: int) -> int:
        return max(3, math.ceil(flashcard_count * 1.5))

    def _average_difficulty(self, flashcards: List[Dict]) -> str:
        if not flashcards:
            return "Medium"
        values = {"Easy": 1, "Medium": 2, "Hard": 3}
        average = sum(values.get(card["difficulty"], 2) for card in flashcards) / len(flashcards)
        if average < 1.7:
            return "Easy"
        if average < 2.35:
            return "Medium"
        return "Hard"

    def _average_confidence(self, flashcards: List[Dict]) -> int:
        if not flashcards:
            return 0
        return round(sum(card["confidence"] for card in flashcards) / len(flashcards))

    def _pipeline_steps(self, status: str = "completed") -> Dict:
        return {
            f"step{index + 1}": {"status": status, "label": label}
            for index, label in enumerate(PIPELINE_TIMELINE)
        }

    def _insights(self, result: Dict) -> Dict:
        return {
            "topic": result["topic"],
            "confidence": result["confidence"],
            "difficulty": result["difficulty"],
            "readingLevel": result["readingLevel"],
            "studyTime": result["studyTime"],
            "readingTime": result["readingTime"],
            "totalWords": result["wordCount"],
            "wordCount": result["wordCount"],
            "totalCharacters": result["characterCount"],
            "questionsGenerated": result["questionCount"],
            "questionCount": result["questionCount"],
            "keywordsCount": len(result["keywords"]),
            "entitiesCount": len([entity for entity in result["entities"] if entity.get("entityType") != "NONE"]),
            "topicsCovered": len(result["topics"]),
            "summary": result["summary"],
            "keywords": result["keywords"],
            "entities": result["entities"],
            "topics": result["topics"],
        }
