# SLOTH - Project Structure & Setup Guide

**Companion document to SLOTH_PROJECT_SPEC.md**

---

## RECOMMENDED PROJECT STRUCTURE

```
sloth/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Environment variables, settings
│   │   ├── database.py        # PostgreSQL connection setup
│   │   │
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── meal_plan.py
│   │   │   ├── ingredient.py
│   │   │   └── weight_entry.py
│   │   │
│   │   ├── schemas/           # Pydantic schemas (API contracts)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── meal_plan.py
│   │   │   └── responses.py
│   │   │
│   │   ├── routers/           # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Login, register, password reset
│   │   │   ├── meal_plans.py  # Browse, filter meal plans
│   │   │   ├── preferences.py # Like/dislike tracking
│   │   │   ├── progress.py    # Weight entries, graphs
│   │   │   ├── grocery.py     # Grocery list generation
│   │   │   └── admin.py       # Admin panel routes
│   │   │
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── meal_service.py
│   │   │   ├── llm_service.py # Claude API integration
│   │   │   └── grocery_service.py
│   │   │
│   │   └── utils/             # Helper functions
│   │       ├── __init__.py
│   │       ├── security.py
│   │       └── validators.py
│   │
│   ├── tests/                 # Backend tests
│   │   ├── test_auth.py
│   │   └── test_meal_plans.py
│   │
│   ├── alembic/               # Database migrations
│   │   └── versions/
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (gitignored)
│   └── README.md
│
├── frontend/                  # React PWA
│   ├── public/
│   │   ├── manifest.json      # PWA manifest
│   │   ├── service-worker.js  # Offline functionality
│   │   └── icons/             # App icons (various sizes)
│   │
│   ├── src/
│   │   ├── main.jsx           # React entry point
│   │   ├── App.jsx            # Root component
│   │   │
│   │   ├── components/        # Reusable UI components
│   │   │   ├── common/
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   └── Spinner.jsx
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Navigation.jsx
│   │   │   │
│   │   │   └── meals/
│   │   │       ├── MealCard.jsx
│   │   │       ├── MealDetail.jsx
│   │   │       └── MealFilter.jsx
│   │   │
│   │   ├── pages/             # Route components
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── MealPlans.jsx
│   │   │   ├── GroceryList.jsx
│   │   │   ├── Progress.jsx
│   │   │   └── Profile.jsx
│   │   │
│   │   ├── services/          # API client
│   │   │   ├── api.js         # Axios setup
│   │   │   ├── authService.js
│   │   │   └── mealService.js
│   │   │
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   └── useMealPlans.js
│   │   │
│   │   ├── context/           # React Context (global state)
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── utils/             # Helper functions
│   │   │   ├── formatters.js
│   │   │   └── validators.js
│   │   │
│   │   └── styles/            # CSS/styling
│   │       └── main.css
│   │
│   ├── package.json           # NPM dependencies
│   ├── vite.config.js         # Vite build config
│   ├── .env                   # Environment variables (gitignored)
│   └── README.md
│
├── docs/                      # Documentation
│   ├── API.md                 # API documentation
│   ├── DATABASE.md            # Database schema docs
│   └── DEPLOYMENT.md          # Deployment guide
│
├── scripts/                   # Utility scripts
│   ├── import_meal_plans.py   # Import 100 meal plans
│   └── seed_database.py       # Dev database seeding
│
├── .gitignore
├── README.md                  # Project overview
└── LICENSE
```

---

## INITIAL SETUP COMMANDS

### Prerequisites
```bash
# Check you have these installed:
python --version    # Should be 3.11 or higher
node --version      # Should be 18 or higher
psql --version      # Should be 14 or higher
git --version       # Any recent version
```

### Step 1: Create Project Repository

```bash
# Create project directory
mkdir sloth
cd sloth

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/
.pytest_cache/

# Node
node_modules/
dist/
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

# Initial commit
git add .gitignore
git commit -m "Initial commit"
```

### Step 2: Set Up Backend

```bash
# Create backend directory
mkdir -p backend
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install FastAPI and dependencies
pip install fastapi[all] sqlalchemy psycopg2-binary alembic python-dotenv

# Create requirements.txt
pip freeze > requirements.txt

# Create basic project structure
mkdir -p app/{models,schemas,routers,services,utils}
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/sloth
SECRET_KEY=your-secret-key-change-this-in-production
CLAUDE_API_KEY=your-claude-api-key
ENVIRONMENT=development
EOF

echo "Backend setup complete!"
```

### Step 3: Set Up Frontend

```bash
# Go back to project root
cd ..

# Create React + Vite app
npm create vite@latest frontend -- --template react
cd frontend

# Install dependencies
npm install

# Install additional packages
npm install react-router-dom axios

# Install PWA plugin
npm install vite-plugin-pwa -D

echo "Frontend setup complete!"
```

### Step 4: Set Up PostgreSQL Database

```bash
# Create database (run in terminal)
psql -U postgres -c "CREATE DATABASE sloth;"
psql -U postgres -c "CREATE USER sloth_user WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sloth TO sloth_user;"

# Update backend/.env with actual credentials
```

### Step 5: Initialize Alembic (Database Migrations)

```bash
cd backend

# Initialize alembic
alembic init alembic

# Edit alembic.ini to use your database URL
# (or better: configure to read from .env)

echo "Database migration setup complete!"
```

---

## DEVELOPMENT WORKFLOW

### Running Backend (Development)

```bash
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Running Frontend (Development)

```bash
cd frontend

# Start dev server
npm run dev

# Access at: http://localhost:5173
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create a new migration after model changes
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when you add them)
cd frontend
npm test
```

---

## ENVIRONMENT VARIABLES

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://sloth_user:password@localhost:5432/sloth

# Security
SECRET_KEY=generate-a-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase Auth
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key

# Claude API
CLAUDE_API_KEY=your-claude-api-key
CLAUDE_MODEL=claude-sonnet-4-20250514

# Environment
ENVIRONMENT=development
DEBUG=True
```

### Frontend (.env)

```bash
# API endpoint
VITE_API_URL=http://localhost:8000

# Supabase (if using client-side auth)
VITE_SUPABASE_URL=your-supabase-project-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

---

## FIRST BACKEND CODE (app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sloth API",
    description="Meal planning SaaS backend",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sloth API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Test it:**
```bash
cd backend
uvicorn app.main:app --reload

# In another terminal:
curl http://localhost:8000
# Should return: {"message": "Sloth API is running"}
```

---

## FIRST FRONTEND CODE (src/App.jsx)

```jsx
import { useState } from 'react'
import './App.css'

function App() {
  const [apiMessage, setApiMessage] = useState('')

  const testAPI = async () => {
    const response = await fetch('http://localhost:8000')
    const data = await response.json()
    setApiMessage(data.message)
  }

  return (
    <div className="App">
      <h1>Sloth Meal Planner</h1>
      <button onClick={testAPI}>Test Backend Connection</button>
      {apiMessage && <p>Backend says: {apiMessage}</p>}
    </div>
  )
}

export default App
```

**Test it:**
```bash
cd frontend
npm run dev

# Visit http://localhost:5173
# Click "Test Backend Connection"
# Should display backend message
```

---

## RAILWAY.APP DEPLOYMENT (When Ready)

### Initial Setup

1. Create account at https://railway.app
2. Install Railway CLI: `npm install -g @railway/cli`
3. Login: `railway login`

### Deploy Backend

```bash
cd backend

# Create new project
railway init

# Add PostgreSQL
railway add

# Deploy
railway up

# Set environment variables in Railway dashboard
```

### Deploy Frontend

```bash
cd frontend

# Build for production
npm run build

# Deploy (or use Railway's GitHub integration)
railway up
```

---

## HELPFUL COMMANDS REFERENCE

```bash
# Backend - Install new package
pip install package-name
pip freeze > requirements.txt

# Frontend - Install new package
npm install package-name

# Database - Connect to PostgreSQL
psql -U sloth_user -d sloth

# Database - View tables
\dt

# Database - Describe table
\d table_name

# Git - Common commands
git status
git add .
git commit -m "Message"
git push

# Python - Format code
pip install black
black .

# Python - Lint code
pip install flake8
flake8 .
```

---

## DEBUGGING CHECKLIST

**Backend won't start:**
- [ ] Virtual environment activated?
- [ ] All dependencies installed? (`pip install -r requirements.txt`)
- [ ] .env file exists and has correct values?
- [ ] PostgreSQL running? (`pg_isready`)
- [ ] Port 8000 not already in use?

**Frontend won't start:**
- [ ] Node modules installed? (`npm install`)
- [ ] Port 5173 not already in use?
- [ ] .env file has correct API URL?

**Database connection fails:**
- [ ] PostgreSQL service running?
- [ ] Database exists? (`psql -l`)
- [ ] User has correct permissions?
- [ ] DATABASE_URL in .env is correct?

**API calls fail from frontend:**
- [ ] Backend server running?
- [ ] CORS middleware configured?
- [ ] API URL correct in frontend .env?
- [ ] Check browser console for errors

---

## LEARNING PROGRESSION

### Week 1-2: Backend Basics
1. Complete FastAPI tutorial (official docs)
2. Build simple CRUD API for meal plans
3. Understand SQLAlchemy models
4. Test with Postman/curl

### Week 3-4: Frontend Basics  
1. Complete React tutorial (react.dev)
2. Build simple component that fetches from API
3. Understand useState, useEffect
4. Create basic routing

### Week 5-6: Integration
1. Connect frontend to backend
2. Implement authentication flow
3. Build meal plan browsing UI
4. Handle loading states and errors

### Week 7-8: Advanced Features
1. Implement user preferences
2. Build grocery list aggregation
3. Add weight tracking
4. Create visualizations

### Week 9-10: Polish
1. PWA configuration
2. Offline functionality
3. Performance optimization
4. Mobile testing

---

## GOTCHAS & COMMON MISTAKES

**FastAPI:**
- Don't forget `async` keyword for database operations
- Always validate input with Pydantic schemas
- Use dependency injection for database sessions

**React:**
- Don't mutate state directly (use setState/setters)
- Remember to add dependencies to useEffect
- Key prop required when mapping arrays to components

**PostgreSQL:**
- Always use parameterized queries (SQLAlchemy does this)
- Don't store passwords in plain text (use hashing)
- Create indexes on frequently queried columns

**PWA:**
- HTTPS required for service workers (except localhost)
- Test on actual mobile device, not just browser devtools
- Service worker cache can cause "old version" issues

---

## NEXT STEPS

**After reading this document:**

1. **Confirm tools installed**
   - Run all commands in "Prerequisites" section
   - Install anything missing

2. **Create project structure**
   - Run setup commands step-by-step
   - Verify each step works before proceeding

3. **Test basic setup**
   - Start backend server
   - Start frontend server
   - Test API connection

4. **Begin learning**
   - Start FastAPI tutorial
   - Build your first endpoint
   - Ask Claude Code when stuck

**Then move to actual feature development.**

---

## RESOURCES

**FastAPI:**
- Official Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/

**React:**
- Official Docs: https://react.dev
- Tutorial: https://react.dev/learn

**PostgreSQL:**
- Tutorial: https://www.postgresqltutorial.com
- Cheat Sheet: https://www.postgresqlcheatsheet.com

**Railway:**
- Docs: https://docs.railway.app
- Templates: https://railway.app/templates

**PWA:**
- Guide: https://web.dev/progressive-web-apps/
- Workbox: https://developers.google.com/web/tools/workbox

---

**You have everything you need. Let's build.**
