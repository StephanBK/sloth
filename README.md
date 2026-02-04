# 🦥 SLOTH - Faultierdiät

> German meal planning SaaS for the "Faultier-Diät" (Sloth Diet) program

[![GitHub](https://img.shields.io/github/license/StephanBK/sloth)](LICENSE)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python-green)](backend/)

## 🎯 What is this?

SLOTH is a web application that helps users follow the "Faultierdiät" meal plan. It provides:

- **14-day meal plans** with 4 difficulty levels
- **Gender-specific plans** (different calorie targets)
- **Weight tracking** with progress visualization
- **Level progression** as users advance through the diet
- **Subscription management** via Stripe

## 🚀 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for blazing fast builds
- **Zustand** for state management
- **React Query** for data fetching
- **PWA** support for mobile

### Backend
- **FastAPI** (Python)
- **Supabase** for auth & database
- **Stripe** for payments
- **SQLAlchemy** + Alembic for ORM/migrations

## 📦 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- Stripe account (for payments)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your Supabase/Stripe credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

## 🔧 Environment Variables

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
DATABASE_URL=your_postgres_connection_string
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_MONTHLY=price_xxx
STRIPE_PRICE_YEARLY=price_xxx
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 📱 Features

- ✅ User authentication (Email + Google OAuth)
- ✅ Multi-step intake form
- ✅ Personalized meal plans
- ✅ Weight tracking with charts
- ✅ Mobile-responsive design
- ✅ Stripe subscription payments
- ✅ PWA support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is private. Contact the owner for licensing information.

## 🙏 Acknowledgments

- Built with Claude Code (Anthropic)
- Meal plans based on the Faultierdiät program
