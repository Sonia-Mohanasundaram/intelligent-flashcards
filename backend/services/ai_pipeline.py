"""AI Processing Pipeline - Main orchestrator"""

import spacy
import logging
from typing import Dict, List, Tuple
import nltk
from nltk.corpus import stopwords
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class AIPipeline:
    """Main AI Processing Pipeline"""
    
    def __init__(self):
        """Initialize AI models"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning("spaCy model not found. Installing...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.stopwords = set(stopwords.words('english'))
    
    def process(self, text: str, title: str = "Untitled") -> Dict:
        """
        Process text through complete AI pipeline
        
        Args:
            text: Input text to process
            title: Note title
        
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Starting AI pipeline for: {title}")
            
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Basic statistics
            word_count, char_count = self._get_statistics(cleaned_text)
            reading_time = self._estimate_reading_time(word_count)
            reading_level = self._classify_reading_level(word_count)
            
            # Process with spaCy
            doc = self.nlp(cleaned_text)
            
            # Extract information
            keywords = self._extract_keywords(doc, cleaned_text)
            entities = self._extract_entities(doc)
            subject = self._detect_subject(keywords, entities)
            topics = self._extract_topics(doc, keywords)
            
            # Generate summary
            summary = self._generate_summary(doc, cleaned_text)
            
            # Generate questions and flashcards
            flashcards = self._generate_flashcards(doc, cleaned_text, keywords, topics, subject)
            
            # Detect difficulty
            difficulty = self._detect_difficulty(word_count, len(keywords), len(entities))
            
            # Calculate confidence
            confidence = self._calculate_confidence(keywords, entities, flashcards)
            
            # Study time estimation
            study_time = self._estimate_study_time(len(flashcards))
            
            result = {
                'success': True,
                'title': title,
                'summary': summary,
                'keywords': keywords,
                'entities': entities,
                'subject': subject,
                'topics': topics,
                'difficulty': difficulty,
                'confidence': confidence,
                'readingTime': reading_time,
                'studyTime': study_time,
                'wordCount': word_count,
                'characterCount': char_count,
                'cardCount': len(flashcards),
                'readingLevel': reading_level,
                'flashcards': flashcards,
                'processedAt': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Pipeline completed. Generated {len(flashcards)} flashcards")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI pipeline: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep punctuation
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text.strip()
    
    def _get_statistics(self, text: str) -> Tuple[int, int]:
        """Get word and character count"""
        words = len(text.split())
        chars = len(text)
        return words, chars
    
    def _estimate_reading_time(self, word_count: int) -> int:
        """Estimate reading time in minutes (average 200 words/minute)"""
        return max(1, round(word_count / 200))
    
    def _classify_reading_level(self, word_count: int) -> str:
        """Classify reading level based on word count"""
        if word_count < 150:
            return "Middle School"
        elif word_count < 400:
            return "High School"
        else:
            return "College"
    
    def _extract_keywords(self, doc, text: str) -> List[str]:
        """Extract important keywords using spaCy and frequency analysis"""
        keywords = []
        
        # Get noun chunks (multi-word terms)
        for chunk in doc.noun_chunks:
            term = chunk.text.lower()
            if len(term.split()) > 1:  # Multi-word chunks
                keywords.append(term.title())
        
        # Get named entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "PERSON"]:
                keywords.append(ent.text)
        
        # Frequency-based keyword extraction
        word_freq = {}
        for token in doc:
            if (token.is_stop or token.is_punct or len(token.text) < 3 or 
                token.pos_ not in ["NOUN", "ADJ", "VERB"]):
                continue
            word = token.lemma_.lower()
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        for word, _ in sorted_words[:10]:
            keywords.append(word.title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        
        return unique_keywords[:15]
    
    def _extract_entities(self, doc) -> List[Dict]:
        """Extract named entities"""
        entities = []
        entity_types = {
            'ORG': 'Organization',
            'PERSON': 'Person',
            'GPE': 'Location',
            'PRODUCT': 'Technology',
            'DATE': 'Date',
            'EVENT': 'Event'
        }
        
        for ent in doc.ents:
            if ent.label_ in entity_types:
                entities.append({
                    'text': ent.text,
                    'type': entity_types.get(ent.label_, ent.label_),
                    'label': ent.label_
                })
        
        # Remove duplicates
        unique_entities = {(e['text'], e['type']): e for e in entities}.values()
        return list(unique_entities)[:10]
    
    def _detect_subject(self, keywords: List[str], entities: List[Dict]) -> str:
        """Detect subject of the text"""
        subject_keywords = {
            'Computer Science': ['java', 'python', 'code', 'algorithm', 'data structure', 'programming', 'software', 'class', 'object', 'jvm'],
            'Mathematics': ['equation', 'theorem', 'calculus', 'integral', 'derivative', 'matrix', 'vector', 'function', 'algebra'],
            'Physics': ['force', 'energy', 'velocity', 'motion', 'gravity', 'quantum', 'newton', 'relativity', 'particle'],
            'Chemistry': ['atom', 'molecule', 'reaction', 'bond', 'element', 'compound', 'acid', 'base', 'chemical'],
            'Biology': ['cell', 'dna', 'rna', 'organism', 'mitosis', 'photosynthesis', 'gene', 'protein', 'evolution'],
            'History': ['war', 'empire', 'king', 'century', 'revolution', 'ancient', 'battle', 'period', 'civilization'],
            'English': ['literature', 'novel', 'poem', 'author', 'character', 'theme', 'narrative', 'grammar'],
            'Business': ['market', 'economy', 'finance', 'investment', 'company', 'management', 'sales', 'profit'],
            'Medicine': ['disease', 'treatment', 'symptom', 'diagnosis', 'medication', 'patient', 'clinical', 'therapy'],
            'Artificial Intelligence': ['neural', 'network', 'machine learning', 'deep learning', 'model', 'training', 'ai', 'algorithm', 'embedding']
        }
        
        text_lower = ' '.join(keywords).lower() + ' ' + ' '.join([e['text'].lower() for e in entities])
        
        scores = {}
        for subject, keywords_list in subject_keywords.items():
            score = sum(text_lower.count(kw.lower()) for kw in keywords_list)
            scores[subject] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "General Knowledge"
    
    def _extract_topics(self, doc, keywords: List[str]) -> List[str]:
        """Extract topics from keywords and entities"""
        topics = []
        
        # Use keywords as topics
        for kw in keywords[:8]:
            topics.append(kw)
        
        return list(dict.fromkeys(topics))[:10]
    
    def _generate_summary(self, doc, text: str) -> List[str]:
        """Generate summary bullet points"""
        sentences = [sent.text.strip() for sent in doc.sents]
        
        if not sentences:
            return ["No summary available"]
        
        # Score sentences based on keyword frequency
        keywords_text = ' '.join([token.text.lower() for token in doc if not token.is_stop and token.is_alpha])
        
        scored_sentences = []
        for sent in sentences:
            if len(sent.split()) > 5:  # Skip very short sentences
                score = sum(1 for word in sent.lower().split() if word in keywords_text)
                scored_sentences.append((sent, score))
        
        # Get top 3-5 sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
        num_summary = min(5, max(3, len(sentences) // 3))
        summary = [sent for sent, _ in top_sentences[:num_summary]]
        
        return summary[:5] if summary else ["Unable to generate summary"]
    
    def _generate_flashcards(self, doc, text: str, keywords: List[str], 
                             topics: List[str], subject: str) -> List[Dict]:
        """Generate flashcard question-answer pairs"""
        flashcards = []
        
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 5]
        
        # Generate Q&A from sentences and keywords
        for i, sentence in enumerate(sentences[:20]):
            keyword = keywords[i % len(keywords)] if keywords else "this concept"
            topic = topics[i % len(topics)] if topics else subject
            
            # Different question templates
            templates = [
                f"What is {keyword}?",
                f"Explain the concept of {keyword}.",
                f"How does {keyword} relate to {subject}?",
                f"Why is {keyword} important?",
                f"Define {keyword} in the context of {subject}.",
            ]
            
            question = templates[i % len(templates)]
            answer = sentence
            
            # Determine difficulty based on sentence complexity
            word_count = len(sentence.split())
            if word_count < 20:
                difficulty = "Easy"
            elif word_count < 40:
                difficulty = "Medium"
            else:
                difficulty = "Hard"
            
            flashcards.append({
                'question': question,
                'answer': answer,
                'difficulty': difficulty,
                'topic': topic,
                'confidence': 75 + (i % 20)  # Vary confidence slightly
            })
        
        return flashcards[:20]  # Return up to 20 flashcards
    
    def _detect_difficulty(self, word_count: int, keyword_count: int, entity_count: int) -> str:
        """Detect overall difficulty level"""
        # Scoring system
        score = 0
        
        if word_count < 150:
            score += 1
        elif word_count < 400:
            score += 2
        else:
            score += 3
        
        if keyword_count < 5:
            score += 1
        elif keyword_count < 15:
            score += 2
        else:
            score += 3
        
        if entity_count < 3:
            score += 1
        else:
            score += 2
        
        if score <= 3:
            return "Easy"
        elif score <= 6:
            return "Medium"
        else:
            return "Hard"
    
    def _calculate_confidence(self, keywords: List[str], entities: List[Dict], 
                             flashcards: List[Dict]) -> int:
        """Calculate AI confidence score (0-100)"""
        score = 70  # Base score
        
        # Add points for keywords
        score += min(15, len(keywords) * 2)
        
        # Add points for entities
        score += min(10, len(entities) * 2)
        
        # Add points for flashcards
        score += min(10, len(flashcards))
        
        return min(100, score)
    
    def _estimate_study_time(self, flashcard_count: int) -> int:
        """Estimate study time in minutes (average 3-5 minutes per card)"""
        return max(5, round(flashcard_count * 2.5))
