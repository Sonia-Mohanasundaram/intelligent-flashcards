# Intelligent Flashcards

A full-stack flashcard learning platform with an AI-powered React/Vite frontend and a Flask backend. This monorepo contains independent frontend and backend projects organized for easy development and GitHub deployment.

## Project Overview

`intelligent-flashcards` bundles:

- **frontend/** — React + Vite web app for creating, reviewing, and managing flashcards
- **backend/** — Flask REST API for authentication, flashcard persistence, and AI processing

## Features

- Email/password signup and login
- Secure password hashing with bcrypt
- JWT-based authentication
- Flashcard generation and review workflows
- Favorites, saved cards, known cards, and statistics
- AI-powered note conversion into flashcards
- Independent frontend and backend development environments

## Folder Structure

```
intelligent-flashcards/
├── backend/          # Flask backend API project
├── frontend/         # React + Vite frontend app
├── README.md
├── .gitignore
└── LICENSE
```

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- TanStack Router
- Tailwind CSS
- Lucide Icons
- React Query
- Sonner notifications

### Backend

- Flask
- MongoDB (via PyMongo)
- JWT authentication
- bcrypt password hashing
- Flask-CORS
- Python 3.9+

## Frontend Setup

1. Open a terminal in `frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the app in your browser at the URL shown by Vite (usually `http://localhost:5173`).

## Backend Setup

1. Open a terminal in `backend/`
2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows CMD:
     ```cmd
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on `.env.example` and set your values.
6. Start the Flask server:
   ```bash
   python run.py
   ```

## Environment Variables

Copy `.env.example` to `.env` in the `backend/` folder and configure:

- `MONGODB_URI` — MongoDB connection string
- `MONGODB_DB_NAME` — Database name
- `JWT_SECRET_KEY` — Secret key for JWT signing
- `JWT_ALGORITHM` — JWT algorithm (e.g. `HS256`)
- `FLASK_ENV` — `development` or `production`
- `FLASK_DEBUG` — `True` or `False`
- `FRONTEND_URL` — Frontend origin allowed by CORS

## Deployment

### Frontend (Vercel)

1. Point Vercel to the repo and set the project directory to `frontend/`.
2. Provide the environment variable `VITE_API_URL` pointing to your deployed backend API, for example:
   ```bash
   https://your-backend.onrender.com/api
   ```
3. Build command: `npm install && npm run build`
4. Output directory: `dist`

### Backend (Render)

1. Point Render to the repo and set the project directory to `backend/`.
2. Build command:
   ```bash
   pip install -r requirements.txt
   ```
3. Start command:
   ```bash
   python run.py
   ```
4. Add environment variables in Render matching `backend/.env.example`.

### MongoDB Atlas

1. Create a MongoDB Atlas cluster.
2. Create a database user and whitelist your backend host.
3. Set `MONGODB_URI` in `backend/.env` or Render environment variables.

## GitHub Ready

This repository is structured as a single full-stack monorepo with independent frontend and backend folders. Use this as the root for GitHub push and deployment.
