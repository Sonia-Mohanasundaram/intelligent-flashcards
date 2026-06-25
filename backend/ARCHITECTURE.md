# 🏗️ Smart Flashcard AI - Architecture & System Design

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SMART FLASHCARD AI SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                USER INTERFACE
                                ━━━━━━━━━━━━━
                    ┌─────────────────────────────────┐
                    │   React Frontend (Vite)          │
                    │  - Dashboard with note input     │
                    │  - 17-Step Progress UI           │
                    │  - Flashcard review              │
                    │  - Study tracking                │
                    └──────────────┬──────────────────┘
                                   │
                              HTTP/JSON
                                   │
        ┌──────────────────────────▼──────────────────────────┐
        │            BACKEND API LAYER                         │
        │          (Flask REST API on Port 5000)              │
        └──────────────────────────┬──────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
    ┌─────▼─────┐          ┌──────▼──────┐          ┌──────▼──────┐
    │   Auth    │          │ Flashcard  │          │  History &  │
    │ Endpoints │          │ Endpoints  │          │  Analytics  │
    └───────────┘          └──────┬──────┘          └─────────────┘
          │                        │
          │            ┌───────────▼─────────────┐
          │            │  17-STEP AI PIPELINE    │
          │            │  ═══════════════════════  │
          │            │  ✅ Text Processing      │
          │            │  ✅ NLP (spaCy)          │
          │            │  ✅ T5 Summarization     │
          │            │  ✅ Question Generation  │
          │            │  ✅ Answer Extraction    │
          │            │  ✅ Scoring              │
          │            │  ✅ Classification       │
          │            └───────────┬─────────────┘
          │                        │
          └────────────────────────┼──────────────────────┐
                                   │                      │
                    ┌──────────────▼──────────┐           │
                    │   SERVICES LAYER         │           │
                    │  - Statistics Service    │           │
                    │  - Export Service        │           │
                    │  - Logging Service       │           │
                    └──────────────┬───────────┘           │
                                   │                       │
                    ┌──────────────▼────────────────┐      │
                    │  PERSISTENCE LAYER            │      │
                    │  ┌──────────────────────────┐ │      │
                    │  │    MongoDB Atlas         │ │      │
                    │  │  (Cloud Database)        │ │      │
                    │  │                          │ │      │
                    │  │  Collections:            │ │      │
                    │  │  • users                 │ │      │
                    │  │  • notes                 │ │      │
                    │  │  • flashcards            │ │      │
                    │  │  • favorites             │ │      │
                    │  │  • history               │ │      │
                    │  │  • statistics            │ │      │
                    │  │  • revision              │ │      │
                    │  └──────────────────────────┘ │      │
                    └────────────────────────────────┘      │
                                                            │
                    ┌───────────────────────────────────────┘
                    │
        ┌───────────▼────────────────┐
        │  EXTERNAL DEPENDENCIES      │
        │  ┌───────────────────────┐ │
        │  │  spaCy 3.7.2          │ │
        │  │ - Tokenization        │ │
        │  │ - NER                 │ │
        │  │ - Dependency parsing  │ │
        │  └───────────────────────┘ │
        │  ┌───────────────────────┐ │
        │  │ Transformers (T5)     │ │
        │  │ - Summarization       │ │
        │  │ - Question Generation │ │
        │  │ - Text-to-Text        │ │
        │  └───────────────────────┘ │
        │  ┌───────────────────────┐ │
        │  │  PyTorch             │ │
        │  │  - Model inference    │ │
        │  │  - GPU support        │ │
        │  └───────────────────────┘ │
        │  ┌───────────────────────┐ │
        │  │ NLTK                  │ │
        │  │ - Stopwords           │ │
        │  │ - Sentence tokenize   │ │
        │  └───────────────────────┘ │
        └─────────────────────────────┘
```

---

## Request Flow: Step-by-Step

### User generates flashcards from notes:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION                                                                │
│    User clicks "Generate Flashcards" with study notes                        │
└──────────────────┬───────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────────────────┐
│ 2. FRONTEND REQUEST                                                           │
│    POST /api/generate                                                        │
│    Headers: Authorization: Bearer {JWT_TOKEN}                                │
│    Body: { text: "...", title: "..." }                                       │
└──────────────────┬───────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────────────────┐
│ 3. BACKEND PROCESSING                                                        │
│    ┌─────────────────────────────────────────────────────────────────────┐  │
│    │ 17-STEP AI PIPELINE EXECUTES:                                       │  │
│    │                                                                     │  │
│    │ Step 1-4: Text Preparation                                         │  │
│    │  • Validate input                                                 │  │
│    │  • Clean text (remove noise)                                      │  │
│    │  • Remove stopwords                                               │  │
│    │  • Tokenize sentences and words                                   │  │
│    │                                                                     │  │
│    │ Step 5-7: Feature Extraction (spaCy)                              │  │
│    │  • Extract keywords (noun chunks, frequency)                      │  │
│    │  • Extract entities (NER: persons, orgs, tech)                    │  │
│    │  • Rank sentences by importance                                   │  │
│    │                                                                     │  │
│    │ Step 8-10: Content Generation (T5)                                │  │
│    │  • Generate 3-5 bullet point summary                              │  │
│    │  • Generate 10-20 questions from top sentences                    │  │
│    │  • Extract answers from original text (NO HALLUCINATION)          │  │
│    │                                                                     │  │
│    │ Step 11-14: Metadata Calculation                                  │  │
│    │  • Detect difficulty (Easy/Medium/Hard)                           │  │
│    │  • Calculate confidence (0-100)                                   │  │
│    │  • Detect subject (10 categories)                                 │  │
│    │  • Extract main topics                                            │  │
│    │                                                                     │  │
│    │ Step 15-17: Finalization                                          │  │
│    │  • Calculate insights (reading time, study time)                  │  │
│    │  • Package flashcards with metadata                               │  │
│    │  • Save to MongoDB                                                │  │
│    └─────────────────────────────────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────────────────┐
│ 4. API RESPONSE                                                               │
│    {                                                                          │
│      "pipelineSteps": { all 17 steps with status },                          │
│      "flashcards": [ Q&A pairs ],                                            │
│      "summary": [ bullet points ],                                           │
│      "keywords": [ extracted keywords ],                                     │
│      "entities": [ named entities ],                                         │
│      "difficulty": "Medium",                                                 │
│      "confidence": 82,                                                       │
│      "subject": "Computer Science",                                          │
│      "topics": [ topics ]                                                    │
│    }                                                                          │
└──────────────────┬───────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────────────────┐
│ 5. FRONTEND DISPLAY                                                           │
│    • Show 17-step progress animation                                         │
│    • Display generated flashcards                                            │
│    • Show summary and insights                                               │
│    • Save to local storage (Zustand)                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Detail View

### Input Processing
```
User Notes Text
    │
    ├─→ [Step 2] Clean Text
    │   └─→ Normalize spaces, punctuation
    │
    ├─→ [Step 3] Remove Stopwords
    │   └─→ Identify 'the', 'a', 'is' (keep text)
    │
    ├─→ [Step 4] Tokenize
    │   └─→ Split into sentences and tokens
    │
    └─→ Clean, Normalized Input Ready
```

### Feature Extraction
```
Processed Text
    │
    ├─→ [Step 5] Keywords (spaCy)
    │   ├─→ Noun chunks: "Java Virtual Machine"
    │   ├─→ Frequency analysis
    │   └─→ 12-15 keywords extracted
    │
    ├─→ [Step 6] Entities (spaCy NER)
    │   ├─→ Person: ["James Gosling"]
    │   ├─→ Organization: ["Sun Microsystems"]
    │   ├─→ Technology: ["Java"]
    │   └─→ 2-8 entities found
    │
    ├─→ [Step 7] Rank Sentences
    │   ├─→ Score by keyword frequency
    │   ├─→ Boost for entities
    │   └─→ Top 10 sentences ranked
    │
    └─→ Keywords, Entities, Ranked Sentences Ready
```

### Content Generation
```
Features → [Step 8] T5 Summarization
    │
    ├─→ Input: Top ranked sentences
    ├─→ Model: t5-small ("summarize: [text]")
    └─→ Output: 3-5 bullet point summary

Features → [Step 9] T5 Question Generation
    │
    ├─→ Input: Top sentences + keywords
    ├─→ Model: t5-small ("generate question: [text]")
    ├─→ Types: definition, explanation, why, how, etc.
    └─→ Output: 10-20 questions

Text + Questions → [Step 10] Answer Extraction
    │
    ├─→ Input: Original text (ONLY)
    ├─→ Match: Find most relevant sentence
    ├─→ Extract: Use original sentence as answer
    └─→ Output: Q&A pairs (NO HALLUCINATION)
```

### Metadata Calculation
```
Q&A Pairs → [Step 11] Difficulty Detection
    │
    ├─→ Question type complexity: definition=1, comparison=3
    ├─→ Answer length complexity
    ├─→ Text complexity (word count)
    ├─→ Entity density
    └─→ Output: Easy, Medium, or Hard

Q&A Pairs → [Step 12] Confidence Score
    │
    ├─→ Base: 70 points
    ├─→ Keywords in text: +10
    ├─→ Entities present: +5
    ├─→ Question quality: +5
    ├─→ Answer quality: +5
    └─→ Output: 0-100 confidence

Text → [Step 13] Subject Detection
    │
    ├─→ Match text to 10 subjects:
    │   Computer Science, Math, Physics, Chemistry,
    │   Biology, History, English, Business, Medicine, AI
    ├─→ Score by keyword frequency
    └─→ Output: "Computer Science" (94% match)

Keywords → [Step 14] Extract Topics
    │
    ├─→ Filter top keywords
    ├─→ Add noun chunks
    ├─→ Remove duplicates
    └─→ Output: 8-12 main topics
```

### Finalization
```
All Data → [Step 15] AI Insights
    │
    ├─→ Reading time: word_count / 200
    ├─→ Study time: flashcard_count * 2.5
    ├─→ Reading level: (complexity based)
    ├─→ Card count: number of flashcards
    └─→ Output: Complete insights object

Insights → [Step 16] Package Flashcards
    │
    ├─→ Question: from T5
    ├─→ Answer: from source text
    ├─→ Difficulty: calculated
    ├─→ Confidence: calculated
    ├─→ Topic: from extraction
    ├─→ Keywords: matched
    └─→ Output: Q&A pair with all metadata

Flashcards → [Step 17] Save to MongoDB
    │
    ├─→ Create Note document
    ├─→ Create Flashcard documents (one per Q&A)
    ├─→ Update user statistics
    ├─→ Log study activity
    └─→ Output: Saved to database ✓
```

---

## Technology Stack Details

### Frontend Stack
```
React 18
├── TanStack Router (routing)
├── Zustand (state management)
├── Vite (build tool)
├── Tailwind CSS (styling)
└── shadcn/ui (components)
```

### Backend Stack
```
Flask 3.0
├── Flask-CORS (cross-origin)
├── PyJWT (authentication)
├── bcrypt (password hashing)
├── pymongo (database)
└── python-dotenv (config)
```

### AI/ML Stack
```
NLP Processing
├── spaCy 3.7.2 (en_core_web_sm model)
│   ├── Tokenization
│   ├── POS tagging
│   ├── Dependency parsing
│   └── Named Entity Recognition
├── Transformers 4.35.2 (Hugging Face)
│   ├── t5-small (summarization, QA)
│   ├── Tokenizer
│   └── Model inference
├── NLTK 3.8.1
│   ├── Stopword removal
│   ├── Punkt tokenizer
│   └── WordNet lemmatization
└── PyTorch 2.0.1
    ├── Model loading
    ├── GPU acceleration (optional)
    └── Tensor operations
```

### Database Stack
```
MongoDB Atlas
├── Cloud-hosted NoSQL
├── Free tier (512 MB)
├── 7 Collections
│   ├── users
│   ├── notes
│   ├── flashcards
│   ├── favorites
│   ├── history
│   ├── statistics
│   └── revision
├── Automatic backups
└── Query indexing
```

---

## Performance Characteristics

### Processing Times
```
Input Size        | Processing Time | CPU | Memory
═════════════════════════════════════════════════════
150 words         | 5-10 sec        | Low | 500 MB
300 words         | 10-20 sec       | Avg | 700 MB
500 words         | 20-40 sec       | Avg | 900 MB
1000+ words       | 40-80 sec       | High| 1.2 GB

Note: First run loads models (~30-60 sec)
      Subsequent runs use cached models (2-3x faster)
```

### Memory Usage
```
Startup
├── Python base: ~50 MB
├── Flask: ~30 MB
├── spaCy model: ~40 MB
├── T5 model: ~240 MB
└── Transformers: ~400 MB
    Total: ~760 MB startup

Per Request
├── Input text: 10-100 KB
├── Tokenization: 50 MB
├── Feature extraction: 100 MB
├── T5 inference: 400 MB
├── Temporary objects: 200 MB
└── Peak: ~1-1.2 GB per request

With Python overhead: 1.5-1.8 GB total
```

### Scalability
```
Single Instance
├── Concurrent requests: 1-2
├── Throughput: 30-60 flashcard sets/hour
├── Response time: 10-40 seconds
└── Memory: 1.5-2 GB

Horizontal Scaling
├── Load balancer
├── Multiple instances
├── Shared MongoDB
└── Scales linearly
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│              SECURITY LAYERS                        │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Network Layer     │
    │  - HTTPS/TLS        │
    │  - CORS whitelisting│
    │  - Rate limiting    │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────────┐
    │   Authentication       │
    │  - JWT tokens (7d exp) │
    │  - Bearer scheme       │
    │  - @token_required     │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │   Password Security    │
    │  - bcrypt hashing      │
    │  - Salt rounds: 10     │
    │  - Never plaintext     │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │   Data Protection      │
    │  - User isolation      │
    │  - Field encryption    │
    │  - Audit logging       │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │   Input Validation     │
    │  - Type checking       │
    │  - Length limits       │
    │  - Injection prevention│
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │   Error Handling       │
    │  - No stack traces     │
    │  - Generic messages    │
    │  - Logged details      │
    └────────────────────────┘
```

---

## Deployment Architecture

### Local Development
```
Developer Machine
├── Python venv
├── spaCy model (cached)
├── T5 model (cached)
├── Flask dev server
├── MongoDB Atlas (cloud)
└── Local browser (Vite)
```

### Docker Deployment
```
Docker Image
├── Base: python:3.11-slim
├── Builder stage
│   ├── Install dependencies
│   ├── Download models
│   └── Build cache
├── Runtime stage
│   ├── Minimal base image
│   ├── Copy built files
│   ├── Install gunicorn
│   └── Start server
└── Size: ~1.2 GB
```

### Production Deployment
```
Render.com / AWS
├── Container runtime
├── Environment variables
├── MongoDB Atlas (cloud)
├── Load balancer
├── Auto-scaling
└── Monitoring & logging
```

---

## API Communication Pattern

```
Frontend                           Backend
   │                                 │
   ├──── POST /api/auth/signup ────→ │
   │                                 ├─ Hash password
   │                                 ├─ Create user
   │                                 ├─ Generate JWT
   │← ─ Token + User Data ─────────┤ │
   │                                 │
   ├──── POST /api/generate ────────→ │
   │     (with JWT)                  │
   │                                 ├─ Verify token
   │                                 ├─ Run 17-step pipeline
   │                                 ├─ Save to MongoDB
   │                                 ├─ Return results
   │←─ Flashcards + Metadata ───────┤ │
   │                                 │
   ├──── GET /api/flashcards ──────→ │
   │     (with JWT)                  │
   │                                 ├─ Verify token
   │                                 ├─ Query MongoDB
   │←─ Flashcard List ──────────────┤ │
```

---

## Summary

This architecture provides:

✅ **Scalability** - Horizontal scaling via containers  
✅ **Security** - Multiple layers of protection  
✅ **Performance** - Optimized with caching  
✅ **Reliability** - Error handling and fallbacks  
✅ **Maintainability** - Clean separation of concerns  
✅ **Observability** - Comprehensive logging  

**Result**: Production-ready AI system for generating intelligent flashcards! 🚀
