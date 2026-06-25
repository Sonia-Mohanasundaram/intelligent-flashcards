# Quick Start Guide

## For Local Development

### 1. First Time Setup (5 minutes)

```bash
# 1. Create Python virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Create .env file
cp .env.example .env

# 6. Edit .env with your MongoDB URI and JWT secret
# Important: Get MongoDB URI from MongoDB Atlas
```

### 2. Running the Backend

```bash
# Make sure virtual environment is activated
python run.py

# Server starts at http://localhost:5000
```

### 3. Testing Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Signup
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'

# Copy the token from response, then test protected endpoint:
# (Replace YOUR_TOKEN with actual token)

# Get profile
curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## For Docker Development

### Using Docker Compose

```bash
# Create .env file first
cp .env.example .env
# Edit .env with your MongoDB URI

# Start backend with Docker
docker-compose up

# Backend available at http://localhost:5000
```

## For Production Deployment (Render.com)

### Step 1: Prepare Repository

```bash
# Make sure all files are committed
git add .
git commit -m "Add Flask backend"
git push origin main
```

### Step 2: Create Render Service

1. Go to [Render.com](https://render.com)
2. Click "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: smart-flashcard-backend
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command**: `gunicorn app:create_app()`
   - **Environment Variables**:
     ```
     FLASK_ENV=production
     MONGODB_URI=your_mongodb_uri_here
     JWT_SECRET_KEY=your_secret_key_here
     FRONTEND_URL=your_frontend_url_here
     ```

### Step 3: Deploy

- Click "Create Web Service"
- Wait for deployment to complete
- Your backend URL will be shown (e.g., https://smart-flashcard-backend.onrender.com)

### Step 4: Update Frontend

Update your frontend to use the production backend URL instead of localhost.

## Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `MONGODB_URI` | Database connection string | `mongodb+srv://user:pass@cluster.mongodb.net/db` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Generate a random string, keep it secret! |
| `JWT_ALGORITHM` | Algorithm for JWT | `HS256` (don't change) |
| `FLASK_ENV` | Environment mode | `development` or `production` |
| `FLASK_DEBUG` | Enable debug mode | `True` or `False` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `SERVER_HOST` | Server host | `0.0.0.0` |
| `SERVER_PORT` | Server port | `5000` |

## MongoDB Atlas Setup (Free Tier)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create account
3. Create Organization and Project
4. Click "Build a Database"
5. Choose Free M0 cluster
6. Select provider and region
7. Create Database User (username and password)
8. Add your IP to Network Access (or use 0.0.0.0/0 for development)
9. Click "Connect" and copy connection string
10. Replace `<password>` in the connection string
11. Add to `.env` as `MONGODB_URI`

## Useful Commands

```bash
# View logs
tail -f app.log

# Run with specific host/port
python run.py --host 0.0.0.0 --port 8000

# Generate new JWT secret
python -c "import secrets; print(secrets.token_hex(32))"

# Check Python version
python --version

# Deactivate virtual environment
deactivate

# Install specific package
pip install package_name

# Update all packages
pip install --upgrade -r requirements.txt
```

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Make sure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: MONGODB_URI not recognized
**Solution**: Create `.env` file in project root with all required variables

### Issue: spaCy model error
**Solution**: Download the model
```bash
python -m spacy download en_core_web_sm
```

### Issue: Port already in use
**Solution**: Use different port
```bash
python run.py  # or modify SERVER_PORT in .env
```

### Issue: CORS errors from frontend
**Solution**: Update `FRONTEND_URL` in `.env` to match your frontend URL

## API Documentation

See [README.md](README.md) for complete API documentation.

## File Structure

```
smart-flashcard-backend/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── run.py                 # Entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose config
├── render.yaml            # Render.com config
├── README.md              # Full documentation
├── routes/                # API routes
│   ├── auth.py            # Authentication endpoints
│   ├── flashcards.py      # Flashcard endpoints
│   ├── history.py         # History endpoints
│   ├── statistics.py      # Statistics endpoints
│   ├── export.py          # Export endpoints
│   └── settings.py        # Settings endpoints
├── models/                # Database models
│   ├── user.py            # User model
│   ├── note.py            # Note model
│   └── flashcard.py       # Flashcard model
├── services/              # Business logic
│   ├── ai_pipeline.py     # AI processing
│   ├── statistics.py      # Statistics service
│   └── export.py          # Export service
├── middleware/            # Middleware
│   └── jwt_handler.py     # JWT authentication
└── utils/                 # Utilities
    ├── database.py        # Database initialization
    └── helpers.py         # Helper functions
```

## Next Steps

1. ✅ Setup environment (`.env` file)
2. ✅ Install dependencies (`pip install -r requirements.txt`)
3. ✅ Download spaCy model (`python -m spacy download en_core_web_sm`)
4. ✅ Run locally (`python run.py`)
5. ✅ Test endpoints (see Testing section above)
6. ✅ Connect frontend (update API URL)
7. ✅ Deploy to production (Render.com)

## Support

For detailed API documentation, see [README.md](README.md)
