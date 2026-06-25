# Smart Flashcard AI - Backend

A production-ready Flask backend for the Smart Flashcard AI EdTech platform. This backend provides REST APIs for intelligent flashcard generation using local NLP/ML models (no external APIs).

## Features

✅ **User Authentication** - Secure signup/login with JWT tokens and bcrypt password hashing  
✅ **AI-Powered Flashcard Generation** - Generate flashcards from notes using spaCy and Hugging Face  
✅ **Local AI Processing** - All NLP processing runs locally (no external AI APIs)  
✅ **MongoDB Integration** - Persistent data storage with MongoDB Atlas  
✅ **RESTful API** - Complete REST API for all operations  
✅ **Statistics & Analytics** - Comprehensive user statistics and progress tracking  
✅ **Export Features** - Export flashcards as JSON, CSV, or PDF-ready format  
✅ **Production Ready** - Deployable on Render, Railway, or similar platforms  

## Tech Stack

- **Backend Framework**: Flask 3.0
- **Database**: MongoDB Atlas (free tier)
- **Authentication**: JWT + bcrypt
- **NLP/ML**: spaCy, Hugging Face Transformers
- **Deployment**: Render.com (recommended)

## Installation

### 1. Prerequisites

- Python 3.9+
- MongoDB Atlas account (free tier)
- Git

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd smart-flashcard-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/smartflashcard?retryWrites=true&w=majority
MONGODB_DB_NAME=smartflashcard

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this
JWT_ALGORITHM=HS256

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# CORS Configuration
FRONTEND_URL=http://localhost:5173

# Server Configuration
SERVER_PORT=5000
SERVER_HOST=0.0.0.0
```

### 4. MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account
3. Create a cluster
4. Create a database user with username and password
5. Get your connection string and add it to `.env`

## Running the Backend

### Development

```bash
python run.py
```

The server will start at `http://localhost:5000`

### Production

For production deployment on Render:

1. Create new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables from your `.env`
4. Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
5. Start command: `python run.py`

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}

Response: { token, user: { id, email, name } }
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: { token, user: { id, email, name } }
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>

Response: { user: { id, email, name, createdAt } }
```

#### Update Profile (Name only)
```http
PUT /api/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jane Doe"
}

Response: { message, user: { id, email, name } }
```

#### Change Password
```http
PUT /api/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "oldPassword": "password123",
  "newPassword": "newpassword123"
}

Response: { message }
```

### Flashcard Endpoints

#### Generate Flashcards (AI Processing)
```http
POST /api/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Java is a high-level, class-based programming language...",
  "title": "Java Basics"
}

Response: {
  message,
  note: { id, title, subject, topics, ... },
  summary: [...],
  keywords: [...],
  entities: [...],
  flashcards: [
    { question, answer, difficulty, confidence, topic },
    ...
  ],
  stats: { wordCount, readingTime, studyTime, confidence, ... }
}
```

#### Get All Flashcards
```http
GET /api/flashcards?skip=0&limit=50&difficulty=Medium&known=false
Authorization: Bearer <token>

Response: { flashcards: [...], stats: { total, known, notKnown, ... } }
```

#### Get Single Flashcard
```http
GET /api/flashcards/<flashcard_id>
Authorization: Bearer <token>

Response: { flashcard: { ...} }
```

#### Mark Flashcard as Known/Not Known
```http
PUT /api/flashcards/<flashcard_id>/known
Authorization: Bearer <token>
Content-Type: application/json

{
  "known": true
}

Response: { message, flashcard: {...} }
```

#### Add to Favorites
```http
POST /api/flashcards/<flashcard_id>/favorite
Authorization: Bearer <token>

Response: { message, flashcard: {...} }
```

#### Remove from Favorites
```http
DELETE /api/flashcards/<flashcard_id>/favorite
Authorization: Bearer <token>

Response: { message, flashcard: {...} }
```

#### Delete Flashcard
```http
DELETE /api/flashcards/<flashcard_id>
Authorization: Bearer <token>

Response: { message }
```

#### Get Favorites
```http
GET /api/favorites?skip=0&limit=50
Authorization: Bearer <token>

Response: { favorites: [...] }
```

### History Endpoints

#### Get Note History
```http
GET /api/history?skip=0&limit=50&search=query&subject=Biology
Authorization: Bearer <token>

Response: { history: [...] }
```

#### Get Single Note
```http
GET /api/history/<note_id>
Authorization: Bearer <token>

Response: { note: {...} }
```

#### Rename Note
```http
PUT /api/history/<note_id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "New Title"
}

Response: { message, note: {...} }
```

#### Delete Note
```http
DELETE /api/history/<note_id>
Authorization: Bearer <token>

Response: { message }
```

#### Get All Subjects
```http
GET /api/history/subjects
Authorization: Bearer <token>

Response: { subjects: [...] }
```

#### Get All Topics
```http
GET /api/history/topics
Authorization: Bearer <token>

Response: { topics: [...] }
```

### Statistics Endpoints

#### Get Dashboard Statistics
```http
GET /api/statistics
Authorization: Bearer <token>

Response: {
  statistics: {
    cards: { total, known, notKnown, revision, favorite },
    notes: { total },
    completion: 45.5,
    avgConfidence: 82.3,
    avgDifficulty: "Medium",
    subjectDistribution: { "Biology": 5, "Physics": 3, ... },
    difficultyDistribution: { "Easy": 2, "Medium": 4, "Hard": 1 },
    weeklyActivity: 12,
    streak: 5
  }
}
```

#### Get Subject Statistics
```http
GET /api/statistics/subject/<subject>
Authorization: Bearer <token>

Response: {
  statistics: {
    subject: "Biology",
    notes: 3,
    cards: 15,
    known: 10,
    favorite: 2,
    avgConfidence: 85.5
  }
}
```

### Export Endpoints

#### Export as JSON
```http
GET /api/export/json?noteId=<optional_note_id>
Authorization: Bearer <token>

Response: {
  exportDate: "2024-01-15T...",
  flashcards: [...]
}
```

#### Export as CSV
```http
GET /api/export/csv?noteId=<optional_note_id>
Authorization: Bearer <token>

Response: CSV file download
```

#### Get PDF Export Data
```http
GET /api/export/pdf-data?noteId=<optional_note_id>
Authorization: Bearer <token>

Response: {
  title: "...",
  exportDate: "...",
  totalCards: 20,
  byTopic: {...},
  summary: { easy, medium, hard, known, favorite }
}
```

### Settings Endpoints

#### Get Settings
```http
GET /api/settings
Authorization: Bearer <token>

Response: {
  settings: {
    fullName: "John Doe",
    email: "john@example.com",
    createdAt: "2024-01-01T..."
  }
}
```

#### Update Settings (Name only)
```http
PUT /api/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "fullName": "Jane Doe"
}

Response: { message, settings: {...} }
```

### Health Check

```http
GET /api/health

Response: { status: "ok", message: "...", version: "1.0.0" }
```

## AI Processing Pipeline

The backend uses a sophisticated local NLP pipeline:

1. **Text Cleaning** - Normalize and clean input text
2. **Tokenization** - Split text into sentences and tokens
3. **Keyword Extraction** - Extract important terms using spaCy
4. **Named Entity Recognition** - Identify people, organizations, locations, etc.
5. **Subject Detection** - Classify the subject of the notes
6. **Topic Extraction** - Extract relevant topics
7. **Summary Generation** - Create bullet-point summary
8. **Flashcard Generation** - Generate Q&A pairs from sentences
9. **Difficulty Classification** - Assign difficulty levels
10. **Confidence Scoring** - Calculate AI confidence

All processing happens locally without external APIs.

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password": "hashed_password",
  "name": "John Doe",
  "createdAt": ISODate,
  "updatedAt": ISODate
}
```

### Notes Collection
```json
{
  "_id": ObjectId,
  "userId": ObjectId,
  "title": "Java Basics",
  "subject": "Computer Science",
  "topics": ["OOP", "Classes", "Inheritance"],
  "originalText": "...",
  "summary": ["...", "..."],
  "keywords": ["Class", "Object", "Inheritance"],
  "entities": [{ text: "Java", type: "Technology" }],
  "confidence": 85,
  "difficulty": "Medium",
  "wordCount": 250,
  "readingTime": 2,
  "studyTime": 5,
  "createdAt": ISODate,
  "updatedAt": ISODate
}
```

### Flashcards Collection
```json
{
  "_id": ObjectId,
  "userId": ObjectId,
  "noteId": ObjectId,
  "question": "What is a class?",
  "answer": "A class is a blueprint for creating objects...",
  "difficulty": "Easy",
  "confidence": 82,
  "topic": "OOP",
  "subject": "Computer Science",
  "known": false,
  "favorite": false,
  "revisionPriority": "low",
  "reviewCount": 0,
  "lastReviewedAt": null,
  "createdAt": ISODate,
  "updatedAt": ISODate
}
```

## Error Handling

All endpoints return standard JSON error responses:

```json
{
  "error": "Error message describing the issue"
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Security

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens for authentication
- ✅ CORS configured for frontend
- ✅ Input validation on all endpoints
- ✅ Environment variables for sensitive data
- ✅ MongoDB connection secured

## Deployment

### On Render.com

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Set environment variables:
   - `MONGODB_URI`
   - `JWT_SECRET_KEY`
   - `FLASK_ENV=production`
   - `FRONTEND_URL=<your-frontend-url>`
5. Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
6. Start command: `gunicorn app:create_app()`

### Production Recommendations

- Use production WSGI server (Gunicorn)
- Set strong JWT secret key
- Enable HTTPS
- Set `FLASK_ENV=production`
- Use managed MongoDB instance
- Add monitoring and logging

## Troubleshooting

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### MongoDB Connection Failed
- Check `MONGODB_URI` in `.env`
- Verify MongoDB Atlas IP whitelist
- Check username and password

### CORS Errors
- Update `FRONTEND_URL` in `.env`
- Check `CORS_ORIGINS` in config

### JWT Token Invalid
- Ensure `Authorization: Bearer <token>` header format
- Check token expiration (7 days default)
- Verify `JWT_SECRET_KEY` is consistent

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ for EdTech learners**
