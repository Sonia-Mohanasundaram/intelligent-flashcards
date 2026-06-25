# Quick Start Testing Guide

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas (free tier)
- Git

### Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd e:\task\smart-flashcard-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (first time - ~100MB)
python -m spacy download en_core_web_sm

# Create .env file
echo FLASK_ENV=development > .env
echo MONGODB_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/smartflashcard?retryWrites=true^&w=majority >> .env
echo JWT_SECRET_KEY=your_very_secure_secret_key_here_make_it_long >> .env
echo SERVER_PORT=5000 >> .env
echo FRONTEND_URL=http://localhost:5173 >> .env
```

**Get MongoDB URI:**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a cluster (free tier)
4. Click "Connect" → "Drivers"
5. Copy connection string
6. Replace `<username>:<password>` with your credentials

### Step 2: Start Backend (30 seconds)

```bash
python run.py
```

**Expected output:**
```
============================================================
Smart Flashcard AI Backend
============================================================
Host: 0.0.0.0
Port: 5000
Debug: True
Environment: development
============================================================
```

### Step 3: Test API (2 minutes)

#### Test 1: Health Check
```bash
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{ "status": "healthy", "environment": "development" }
```

#### Test 2: Signup
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "name": "Test User"
  }'
```

**Expected response:**
```json
{
  "message": "Signup successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "_id": "...",
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

**Copy the token! You'll need it for the next test.**

#### Test 3: Generate Flashcards (The 17-Step Pipeline!)

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Java is a high-level, class-based, object-oriented programming language developed by Sun Microsystems in 1995. It is designed to have as few implementation dependencies as possible. Java applications are typically compiled to bytecode that can run on any Java Virtual Machine (JVM) regardless of the underlying computer architecture. Core principles of Java include inheritance, polymorphism, encapsulation, and abstraction. These principles allow developers to build robust and reusable software systems.",
    "title": "Java Basics"
  }'
```

**This will:**
1. Run all 17 processing steps
2. Extract keywords and entities
3. Generate summary
4. Create questions and answers
5. Calculate difficulty and confidence
6. Save to MongoDB
7. Return complete response

**Expected response (abbreviated):**
```json
{
  "message": "Flashcards generated successfully",
  "pipelineSteps": {
    "step1": { "status": "completed" },
    "step2": { "status": "completed" },
    "step3": { "status": "completed" },
    ...
    "step17": { "status": "completed" }
  },
  "summary": [
    "Java is a high-level OOP language created by Sun Microsystems",
    "It compiles to bytecode that runs on any JVM",
    "Core principles: inheritance, polymorphism, encapsulation, abstraction"
  ],
  "subject": "Computer Science",
  "keywords": ["Java", "OOP", "JVM", "bytecode", "inheritance", ...],
  "entities": [
    { "text": "Java", "type": "Technology" },
    { "text": "Sun Microsystems", "type": "Organization" }
  ],
  "difficulty": "Medium",
  "confidence": 82,
  "flashcards": [
    {
      "question": "What is Java?",
      "answer": "Java is a high-level programming language...",
      "difficulty": "Easy",
      "confidence": 85
    },
    {
      "question": "Explain inheritance in Java",
      "answer": "Inheritance is one of the core principles...",
      "difficulty": "Medium",
      "confidence": 80
    },
    // ... more flashcards
  ]
}
```

---

## 🎯 What Each Test Shows

### Test 1: Health Check
✅ Backend is running  
✅ API is responding  
✅ No server errors

### Test 2: Signup
✅ Authentication working  
✅ Password hashing working  
✅ JWT tokens generating  
✅ User creation successful

### Test 3: Generate (The Important One!)
✅ All 17 pipeline steps running  
✅ Keywords extracted using spaCy  
✅ Entities identified using NER  
✅ Questions generated using T5  
✅ Answers from source text (no hallucination)  
✅ Difficulty calculated correctly  
✅ Confidence scores computed  
✅ Subject detected  
✅ Flashcards created and ready  
✅ Data saved to MongoDB  

---

## 🔍 What's Happening in the 17 Steps

When you call the generate endpoint:

```
Step 1: Notes Received → Input processed
Step 2: Cleaning Text → Extra spaces removed
Step 3: Removing Stopwords → Identified (text kept)
Step 4: Tokenizing → Sentences and words split
Step 5: Extracting Keywords → 12 keywords found
Step 6: Extracting Entities → 2 entities identified (Java, Sun)
Step 7: Ranking Sentences → Top 10 sentences scored
Step 8: Generating Summary → 3-5 bullet points created
Step 9: Generating Questions → 12 questions generated
Step 10: Generating Answers → Extracted from source text
Step 11: Difficulty Detection → Easy/Medium/Hard assigned
Step 12: Confidence Score → 0-100 scores calculated
Step 13: Subject Detection → "Computer Science" identified
Step 14: Topics Covered → 8 topics extracted
Step 15: AI Insights → Metrics calculated
Step 16: Flashcards → 12 Q&A pairs packaged
Step 17: Save to Database → Saved to MongoDB ✓
```

---

## 📊 Understanding the Response

### Pipeline Steps
Shows status of each of the 17 steps:
```json
"pipelineSteps": {
  "step1": { "status": "completed", "message": "Notes received successfully" },
  "step2": { "status": "completed", "cleaned_text_length": 2500 },
  // ... all 17 steps
}
```

### Summary
3-5 key bullet points extracted:
```json
"summary": [
  "Java is a high-level OOP language...",
  "It uses JVM for platform independence...",
  "Core principles: inheritance, polymorphism..."
]
```

### Keywords
Main concepts identified:
```json
"keywords": ["Java", "OOP", "JVM", "inheritance", "polymorphism", ...]
```

### Entities
Named entities extracted:
```json
"entities": [
  { "text": "Java", "type": "Technology" },
  { "text": "Sun Microsystems", "type": "Organization" }
]
```

### Flashcards
Generated Q&A pairs:
```json
"flashcards": [
  {
    "question": "What is Java?",
    "answer": "Java is a high-level, class-based...",
    "difficulty": "Easy",
    "confidence": 85,
    "topic": "Java",
    "type": "definition"
  },
  // ... more flashcards
]
```

---

## 🐛 Troubleshooting

### ❌ "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### ❌ "MongoDB connection error"
Check:
- MONGODB_URI is correct in .env
- Your IP is whitelisted in MongoDB Atlas
- Username and password are correct
- Database name is correct

### ❌ "Torch not installed"
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### ❌ "CORS error in frontend"
Add to .env:
```env
FRONTEND_URL=http://localhost:5173
```

### ❌ "T5 model loading slowly"
First time: Normal (models download ~300MB)  
Subsequent times: Much faster (cached)

---

## ✅ Success Indicators

You'll know it's working when:

✅ All 3 curl tests pass  
✅ Response includes all 17 steps with "status": "completed"  
✅ Flashcards have real questions and answers  
✅ Difficulty levels are assigned (Easy/Medium/Hard)  
✅ Confidence scores are 0-100  
✅ Keywords and entities are extracted  
✅ Summary has 3-5 bullet points  
✅ Subject is detected  
✅ No hallucinated answers (all from source text)  

---

## 🎮 Testing the Frontend

### Configure Frontend

In `smart-ai-flash-main/smart-ai-flash-main/.env.local`:
```env
VITE_API_URL=http://localhost:5000/api
```

Or in `src/lib/api.ts`:
```typescript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Start Frontend

```bash
cd smart-ai-flash-main/smart-ai-flash-main
npm install
npm run dev
```

### Test Full Flow

1. Go to `http://localhost:5173`
2. Signup with test account
3. Paste notes into textarea
4. Click "Generate Flashcards"
5. Watch 17-step progress UI
6. See generated flashcards
7. Review and study

---

## 📈 Performance Expectations

| Note Size | Processing Time | Models Loaded |
|-----------|-----------------|---------------|
| 100 words | 3-5 seconds | First time only |
| 200 words | 5-10 seconds | ~1.5 GB memory |
| 300 words | 10-15 seconds | ~500 MB per request |
| 500 words | 20-30 seconds | Cached after first |

---

## 🚀 Next Steps

1. ✅ Run the 3 tests above
2. ✅ Configure MongoDB correctly
3. ✅ Start frontend
4. ✅ Test full flow
5. ✅ Customize difficulty/confidence thresholds
6. ✅ Deploy to production

---

## 💡 Pro Tips

1. **First run is slow** - spaCy and T5 models are loading. Subsequent calls are 2-3x faster.

2. **Use smaller notes initially** - 200-300 words is optimal for testing. Larger notes take longer.

3. **Check MongoDB** - Go to MongoDB Atlas → Collections to see your flashcards being saved in real-time.

4. **Enable debug logs** - Set `FLASK_ENV=development` to see detailed pipeline logs.

5. **Test locally first** - Get everything working before deploying to production.

---

## 📞 Getting Help

**Issue with tests?**
- Check the Troubleshooting section above
- Verify .env is set correctly
- Check backend logs for errors

**Frontend not working?**
- Set VITE_API_URL correctly
- Check browser console for errors
- Verify backend is running

**Flashcards not generating?**
- Check MongoDB connection
- Verify token is valid
- Check backend logs

---

**Ready to test? Follow the 3 tests above and you'll have a working AI pipeline! 🎉**
