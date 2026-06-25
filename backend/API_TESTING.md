# API Testing Guide

This file contains example cURL commands to test all API endpoints.

## Health Check

```bash
curl http://localhost:5000/api/health
```

## Authentication Routes

### 1. Signup (Register New User)

```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Note:** Save the `token` for use in other requests!

---

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response:** Same as signup with new token

---

### 3. Get Profile

Replace `YOUR_TOKEN` with the token from signup/login:

```bash
curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2024-01-15T10:30:00"
  }
}
```

---

### 4. Update Profile (Name Only)

```bash
curl -X PUT http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe"
  }'
```

---

### 5. Change Password

```bash
curl -X PUT http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "oldPassword": "password123",
    "newPassword": "newpassword123"
  }'
```

---

## Flashcard Routes

### 1. Generate Flashcards from Notes (AI Processing)

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Java is a high-level, class-based, object-oriented programming language developed by Sun Microsystems in 1995. It is designed to have as few implementation dependencies as possible. Java applications are typically compiled to bytecode that can run on any Java Virtual Machine (JVM) regardless of the underlying computer architecture. Core principles of Java include inheritance, polymorphism, encapsulation, and abstraction. These principles allow developers to build robust and reusable software systems.",
    "title": "Java Basics"
  }'
```

**Response:**
```json
{
  "message": "Flashcards generated successfully",
  "note": { "id": "...", "title": "Java Basics", ... },
  "summary": ["Java is an OOP language...", "..."],
  "subject": "Computer Science",
  "topics": ["OOP", "Classes", "Inheritance"],
  "keywords": ["Java", "OOP", "Inheritance"],
  "entities": [{ "text": "Java", "type": "Technology" }],
  "difficulty": "Medium",
  "confidence": 85,
  "readingTime": 2,
  "studyTime": 5,
  "cardCount": 15,
  "flashcards": [
    {
      "id": "...",
      "question": "What is Java?",
      "answer": "Java is a high-level, class-based, object-oriented programming language...",
      "difficulty": "Easy",
      "confidence": 82,
      "topic": "OOP"
    }
  ]
}
```

---

### 2. Get All Flashcards

```bash
curl http://localhost:5000/api/flashcards \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**With filters:**

```bash
# Get only Easy difficulty cards
curl "http://localhost:5000/api/flashcards?difficulty=Easy" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only known cards
curl "http://localhost:5000/api/flashcards?known=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only favorites
curl "http://localhost:5000/api/flashcards?favorite=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Pagination
curl "http://localhost:5000/api/flashcards?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "flashcards": [
    {
      "id": "...",
      "question": "What is Java?",
      "answer": "...",
      "difficulty": "Easy",
      "confidence": 82,
      "known": false,
      "favorite": false
    }
  ],
  "stats": {
    "total": 15,
    "known": 5,
    "notKnown": 10,
    "favorite": 2,
    "completion": 33.33,
    "avgConfidence": 82.5,
    "difficulty": { "Easy": 5, "Medium": 7, "Hard": 3 }
  }
}
```

---

### 3. Get Single Flashcard

```bash
curl http://localhost:5000/api/flashcards/FLASHCARD_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Mark Flashcard as Known

```bash
curl -X PUT http://localhost:5000/api/flashcards/FLASHCARD_ID/known \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"known": true}'
```

---

### 5. Add to Favorites

```bash
curl -X POST http://localhost:5000/api/flashcards/FLASHCARD_ID/favorite \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 6. Remove from Favorites

```bash
curl -X DELETE http://localhost:5000/api/flashcards/FLASHCARD_ID/favorite \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 7. Delete Flashcard

```bash
curl -X DELETE http://localhost:5000/api/flashcards/FLASHCARD_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 8. Get Favorites

```bash
curl http://localhost:5000/api/favorites \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## History Routes

### 1. Get Note History

```bash
curl http://localhost:5000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"

# With search
curl "http://localhost:5000/api/history?search=java" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by subject
curl "http://localhost:5000/api/history?subject=Computer%20Science" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Get Single Note

```bash
curl http://localhost:5000/api/history/NOTE_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Rename Note

```bash
curl -X PUT http://localhost:5000/api/history/NOTE_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title"}'
```

---

### 4. Delete Note

```bash
curl -X DELETE http://localhost:5000/api/history/NOTE_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. Get All Subjects

```bash
curl http://localhost:5000/api/history/subjects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** `["Computer Science", "Biology", "Physics"]`

---

### 6. Get All Topics

```bash
curl http://localhost:5000/api/history/topics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** `["OOP", "Classes", "Inheritance", "Polymorphism"]`

---

## Statistics Routes

### 1. Get Dashboard Statistics

```bash
curl http://localhost:5000/api/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "statistics": {
    "cards": {
      "total": 50,
      "known": 30,
      "notKnown": 20,
      "revision": 5,
      "favorite": 8
    },
    "notes": {
      "total": 5
    },
    "completion": 60.0,
    "avgConfidence": 82.5,
    "avgDifficulty": "Medium",
    "subjectDistribution": {
      "Computer Science": 30,
      "Biology": 20
    },
    "difficultyDistribution": {
      "Easy": 15,
      "Medium": 25,
      "Hard": 10
    },
    "weeklyActivity": 12,
    "streak": 5
  }
}
```

---

### 2. Get Subject Statistics

```bash
curl http://localhost:5000/api/statistics/subject/Computer%20Science \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Export Routes

### 1. Export as JSON

```bash
curl http://localhost:5000/api/export/json \
  -H "Authorization: Bearer YOUR_TOKEN" \
  > flashcards.json

# Export specific note
curl "http://localhost:5000/api/export/json?noteId=NOTE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  > flashcards.json
```

---

### 2. Export as CSV

```bash
curl http://localhost:5000/api/export/csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  > flashcards.csv

# Export specific note
curl "http://localhost:5000/api/export/csv?noteId=NOTE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  > flashcards.csv
```

---

### 3. Get PDF Export Data

```bash
curl http://localhost:5000/api/export/pdf-data \
  -H "Authorization: Bearer YOUR_TOKEN"

# Export specific note
curl "http://localhost:5000/api/export/pdf-data?noteId=NOTE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Settings Routes

### 1. Get Settings

```bash
curl http://localhost:5000/api/settings \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Update Settings (Name Only)

```bash
curl -X PUT http://localhost:5000/api/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fullName": "New Name"}'
```

---

## Using Postman or Insomnia

Instead of cURL, you can import and use:

1. **Postman**: Import as collection
2. **Insomnia**: Import as environment

Create a `postman_collection.json` with all the requests above.

---

## Troubleshooting

### 401 Unauthorized
- Make sure you're using the correct token
- Token might be expired (valid for 7 days)
- Check token format: `Authorization: Bearer <token>`

### 400 Bad Request
- Check JSON format is valid
- Verify all required fields are present
- Check Content-Type header is `application/json`

### 404 Not Found
- Resource ID might be incorrect
- Try getting the list to find correct IDs

### 500 Internal Server Error
- Check backend logs (`app.log`)
- Verify MongoDB connection
- Check `.env` configuration

---

**Happy Testing! 🎉**
