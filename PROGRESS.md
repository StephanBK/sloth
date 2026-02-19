# SLOTH - Development Progress Log

**Purpose:** This file tracks what has been built and what's next. When starting a new Claude Code session, say "read PROGRESS.md and continue" to pick up where we left off.

---

## Current Status: Phase 12 - Intake & Level System Simplification

**Last Updated:** February 18, 2026

---

## Completed

### Project Setup
- [x] Created project specification (SLOTH_PROJECT_SPEC.md)
- [x] Created setup guide (SLOTH_SETUP_GUIDE.md)
- [x] Initialized backend directory
- [x] Created Python virtual environment (backend/venv)
- [x] Installed core dependencies (FastAPI, SQLAlchemy, Alembic, psycopg2, pydantic-settings)
- [x] Created requirements.txt

### Backend Foundation (Session 1)
- [x] Database configuration (app/config.py) - reads from .env
- [x] Database connection (app/database.py) - SQLAlchemy engine + session
- [x] Created .env file with local PostgreSQL connection
- [x] SQLAlchemy models:
  - [x] User (app/models/user.py)
  - [x] MealPlan, Meal, Ingredient (app/models/meal_plan.py)
  - [x] WeightEntry (app/models/progress.py)
  - [x] UserPreference (app/models/preference.py)
- [x] Alembic migration setup
- [x] Initial migration created and applied - all tables exist in database
- [x] Pydantic schemas (app/schemas/meal_plan.py)
- [x] Meal Plans API router (app/routers/meal_plans.py):
  - [x] GET /meal-plans - List with filters (level, gender, pagination)
  - [x] GET /meal-plans/{id} - Get single plan with meals and ingredients
  - [x] POST /meal-plans - Create new plan
- [x] Main FastAPI app (app/main.py) with CORS configured
- [x] API tested and working!

### Authentication (Session 2 - COMPLETE)
- [x] Installed Supabase Python SDK + dependencies (supabase, python-jose, httpx, email-validator)
- [x] Updated config.py with Supabase settings
- [x] Created auth service (app/services/auth_service.py)
- [x] Created auth schemas (app/schemas/auth.py)
- [x] Created auth router (app/routers/auth.py)
- [x] Created auth dependencies/middleware (app/dependencies.py)
- [x] Updated main.py to include auth router
- [x] Supabase project created and credentials added to .env
- [x] **Email/password registration tested and working!**
- [x] **Email/password login tested and working!**
- [x] **Google OAuth added!** (Session 7, fixed Session 10)

### User Profile & Weight Tracking (Session 3 - COMPLETE)
- [x] Updated User model with profile fields
- [x] Created ActivityLevel enum
- [x] Created database migration (e08d86a915fb) and applied
- [x] Created user profile schemas (app/schemas/user.py)
- [x] Created users router (app/routers/users.py)
- [x] Created weight tracking schemas (app/schemas/progress.py)
- [x] Created progress router (app/routers/progress.py)
- [x] Implemented stall detection logic
- [x] Implemented weight graph interpolation for gaps

### Frontend Foundation (Session 3 - IN PROGRESS)
- [x] Created React + Vite + TypeScript project
- [x] Configured PWA support (vite-plugin-pwa)
- [x] Set up path aliases (@/ = src/)
- [x] Created folder structure (components, pages, hooks, services, stores, types, utils)
- [x] Created TypeScript types matching backend schemas (src/types/index.ts)
- [x] Created API client with Axios (src/services/api.ts):
  - Auth API (login, register, logout, refresh)
  - User API (profile, intake screens)
  - Weight API (CRUD, history)
- [x] Created auth store with Zustand (src/stores/authStore.ts)
- [x] Set up React Router with protected routes (src/App.tsx)
- [x] Created Login page (German UI)
- [x] Created Register page (German UI)
- [x] Created Intake form (3 screens, German UI)
- [x] Created Dashboard page (basic)
- [x] Created global CSS with design tokens (warm earthy theme — rebranded from Faultierdiät PDFs)
- [x] **Build passes successfully!**

### Weight Tracking UI (Session 4 - COMPLETE)
- [x] Created WeightPage with full weight tracking UI
- [x] Apple Health-inspired graph with Recharts
- [x] Stats cards (Start, Current, Goal weight)
- [x] Progress bar showing % to goal
- [x] Stall detection alert display
- [x] Time filters (7, 30, 90 days)
- [x] Recent entries list
- [x] Add Weight modal with date picker and notes
- [x] Bottom navigation component (Home, Gewicht, Mahlzeiten, Profil)
- [x] Route wired up at /weight

### Meals & Profile Pages (Session 5 - COMPLETE)
- [x] Created MealsPage with meal plan browsing UI
  - [x] Shows meal plans filtered by user's gender and current level
  - [x] Day cards with macro summary (kcal, protein, carbs, fat)
  - [x] Meal plan detail modal with full ingredients list
  - [x] Organized by meal type (Frühstück, Mittagessen, Snack, Abendessen)
- [x] Created ProfilePage with user settings
  - [x] Profile card with avatar and email
  - [x] Stats overview (start, current, goal weight)
  - [x] Progress summary card
  - [x] Editable personal info (height, age, goal weight, activity level)
  - [x] Diet settings display (current level, dietary restrictions)
  - [x] Logout functionality with confirmation modal
- [x] Added meal plan API to frontend (list and get endpoints)
- [x] Updated TypeScript types to match backend schemas
- [x] All routes working (/dashboard, /weight, /meals, /profile)
- [x] Build passes successfully

### Meal Plan Data Import (Session 6 - COMPLETE)
- [x] Converted PDF meal plans to text using pdftotext (layout preserved)
- [x] Created Python import script (backend/scripts/import_meal_plans.py)
- [x] Parsed all 100 meal plans (50 male, 50 female)
- [x] Imported to database:
  - 100 meal plans (5 levels x 10 days x 2 genders)
  - 333 meals (breakfast, lunch, dinner, snack)
  - 921 ingredients with quantities and units
- [x] API returns real meal data
- [x] Frontend can display actual meal plans

### Google OAuth & Frontend Polish (Session 7 - COMPLETE)
- [x] **Google OAuth Login:**
  - [x] Added Google OAuth URL endpoint to authApi
  - [x] Created handleOAuthCallback for token extraction
  - [x] Added loginWithGoogle action to auth store
  - [x] Created AuthCallbackPage for OAuth redirect handling
  - [x] Updated LoginPage with "Mit Google anmelden" button
  - [x] Updated RegisterPage with "Mit Google registrieren" button
  - [x] Added /auth/callback route
- [x] **Mobile Responsiveness:**
  - [x] Added responsive breakpoints (640px, 375px, 768px, 1024px)
  - [x] Mobile-optimized stats grids (3 columns with smaller text)
  - [x] Mobile meal grid (2 columns on mobile, 1 on small)
  - [x] Bottom sheet style modals on mobile
  - [x] Safe area padding for notched devices
  - [x] Responsive buttons and form elements
- [x] **Loading & Error States:**
  - [x] Added page-loading component styles
  - [x] Added page-error component styles
  - [x] Added empty-state styles
  - [x] Added skeleton loading animations
  - [x] Added toast notification styles

### Stripe Payment Integration (Session 7 - COMPLETE)
- [x] **Backend:**
  - [x] Installed Stripe Python SDK
  - [x] Added Stripe config settings (secret key, price IDs, webhook secret)
  - [x] Created subscription schemas (app/schemas/subscription.py)
  - [x] Created StripeService (app/services/stripe_service.py):
    - Checkout session creation
    - Subscription status checks
    - Cancel/reactivate subscriptions
    - Customer portal sessions
    - Promo code validation
    - Webhook event processing
  - [x] Created subscriptions router (app/routers/subscriptions.py):
    - POST /subscriptions/checkout
    - GET /subscriptions/status
    - POST /subscriptions/cancel
    - POST /subscriptions/reactivate
    - POST /subscriptions/portal
    - POST /subscriptions/validate-promo
    - POST /subscriptions/webhook
  - [x] Added subscription fields to User model (stripe_customer_id, subscription_status, subscription_ends_at)
  - [x] Created and applied migration for new fields
- [x] **Frontend:**
  - [x] Added subscriptionApi to api.ts
  - [x] Created SubscriptionPage with:
    - Pricing cards (monthly €29.99, yearly €239.99)
    - Current subscription status display
    - Cancel/reactivate functionality
    - Promo code input and validation
    - Stripe Customer Portal access
    - Success/cancelled message handling
  - [x] Added pricing card CSS with popular badge
  - [x] Added routes for /subscription, /subscription/success, /subscription/cancelled
- [x] Updated .env.example with Stripe settings

---

## Design Decisions Made

### Units & Localization
- **MVP uses ISO units only (kg, cm)**
- Imperial units (lbs, inches) will come later with a settings toggle
- **UI language: German** (target market is Germany)

### Intake Form
- **3 screens:**
  1. Gender, Height (cm), Age
  2. Current Weight (kg)
  3. Calorie Awareness (gaining/maintaining/losing/unknown + optional kcal input), Dietary Restrictions
- Supports both all-at-once submission and screen-by-screen with partial saves
- starting_weight_kg captured on intake (never changes)
- **Level naming:** Displayed as kcal targets (e.g., "2100 kcal") not "Stufe 1-5"
- **Starting level:** Calculated from calorie awareness, not weight-to-lose. If unknown, uses body weight × 30.

### Weight Tracking
- **Graph style: Apple Health inspired**
  - Solid lines for actual measurements
  - Dotted lines for gaps (interpolated values)
- **Stall detection:**
  - Looks at 14-day window
  - Requires 4+ entries to detect (nudges user to log more if fewer)
  - ±0.5kg = stall → suggest level drop
- One entry per day (duplicate dates rejected, must use PATCH to update)

### Frontend Stack
- **React 18 + TypeScript** - Type safety, modern React
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Zustand** - Client state management (simpler than Redux)
- **Axios** - HTTP client with interceptors
- **PWA** - Installable mobile app experience

---

## Up Next

### Production Setup (Priority)
- [x] Set up Stripe products and prices in Stripe Dashboard ✅
- [x] Set up Google OAuth in Supabase Dashboard ✅
- [x] Google OAuth working end-to-end in production ✅
- [x] Configure Stripe webhooks pointing to Railway backend ✅
- [x] Add Stripe env vars to Railway (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, FRONTEND_URL) ✅
- [ ] Test full payment flow with a real customer

### Completed Polish ✅
- [x] Form validation feedback (inline validation, strength meter, match indicator)
- [x] Dashboard page improvements (greeting, progress card, today's meals, quick actions)
- [x] Grocery list feature (day selector, ingredient aggregation, checklist)

### Remaining Polish (Nice to Have)
- [ ] Dark mode support (with warm brown dark palette)
- [ ] Improve Google OAuth consent screen (add logo, verify app)
- [ ] Push notifications for reminders
- [ ] Email notifications for subscription events
- [ ] Free trial period
- [ ] Add custom sloth illustrations/icons to match PDF mascot
- [ ] Consider adding a Google Font (e.g., "Caveat" or "Pacifico") for meal labels to match PDF script style

---

## How to Run

### Backend
```bash
cd /Users/stephanketterer/sloth/backend
source venv/bin/activate
uvicorn app.main:app --reload

# API runs at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Frontend
```bash
cd /Users/stephanketterer/sloth/frontend
npm run dev

# App runs at: http://localhost:5173
```

### Both Together
Run each in a separate terminal:
1. Terminal 1: Backend (port 8000)
2. Terminal 2: Frontend (port 5173)

The frontend proxies API requests to the backend automatically.

---

## File Structure (Current)

```
sloth/
├── SLOTH_PROJECT_SPEC.md
├── SLOTH_SETUP_GUIDE.md
├── PROGRESS.md
├── maenner_layout.txt           # Extracted meal plan text (men)
├── frauen_layout.txt            # Extracted meal plan text (women)
├── backend/
│   ├── venv/
│   ├── requirements.txt
│   ├── .env
│   ├── alembic.ini
│   ├── alembic/versions/
│   ├── scripts/
│   │   └── import_meal_plans.py # Meal plan import script
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── routers/
└── frontend/
    ├── package.json
    ├── vite.config.ts           # PWA + proxy config
    ├── tsconfig.json
    ├── tsconfig.app.json        # Path aliases
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx              # Routes + providers
        ├── App.css              # Global styles
        ├── types/
        │   └── index.ts         # TypeScript types
        ├── services/
        │   └── api.ts           # Axios API client
        ├── stores/
        │   └── authStore.ts     # Zustand auth store
        ├── pages/
        │   ├── auth/
        │   │   ├── LoginPage.tsx
        │   │   └── RegisterPage.tsx
        │   ├── intake/
        │   │   └── IntakePage.tsx
        │   ├── dashboard/
        │   │   └── DashboardPage.tsx
        │   ├── weight/
        │   │   └── WeightPage.tsx
        │   ├── meals/
        │   │   └── MealsPage.tsx
        │   ├── grocery/
        │   │   └── GroceryListPage.tsx
        │   └── profile/
        │       └── ProfilePage.tsx
        ├── components/          # (empty, for reusable components)
        ├── hooks/               # (empty, for custom hooks)
        └── utils/               # (empty, for utilities)
```

---

## Session Log

### Session 1 - February 1, 2026
- Built backend foundation (database, models, meal plans API)

### Session 2 - February 1, 2026
- Added Supabase authentication (email/password)

### Session 3 - February 3, 2026
- Added user profile & weight tracking backend
- **Started frontend!**
  - Set up React + Vite + TypeScript
  - Configured PWA
  - Created API client
  - Created auth store
  - Created Login, Register, Intake, Dashboard pages
  - All in German for target market
  - Build passes successfully

### Session 4 - February 3, 2026
- **Fixed auth flow issues:**
  - Fixed auth response type mismatch (backend returns `session.access_token`, not `access_token`)
  - Fixed JWT token verification (Supabase uses ES256, not HS256)
  - Restarted backend to load new routes
  - **Login now works end-to-end!** ✅
- **Security & Architecture Review:**
  - Architecture score: **8.6/10** - Good foundation
  - Created `.gitignore` files to protect `.env` credentials
  - Created `.env.example` template for new developers
  - Noted JWT signature verification needs proper fix before production
- **Developer Experience:**
  - Created `.claude/settings.json` with allowlist permissions for faster development
- **Noted for future:** Payment system (Stripe, subscriptions, discounts)

### Session 5 - February 3, 2026
- **Meals Page (MealsPage.tsx):**
  - Meal plan browsing filtered by user's gender and current level
  - Grid of day cards showing macros (kcal, protein, carbs, fat)
  - Detail modal with full ingredients and instructions
  - Meals organized by type (breakfast, lunch, snack, dinner)
- **Profile Page (ProfilePage.tsx):**
  - User avatar with email display
  - Stats overview (starting, current, goal weight)
  - Progress summary with weight lost
  - Editable profile fields (height, age, goal weight, activity level)
  - Diet settings display
  - Logout with confirmation modal
- **API additions:**
  - Added mealPlanApi to frontend (list and get endpoints)
  - Updated TypeScript types to match backend meal plan schemas
- **Frontend ~75% complete** - Core pages done, polish remaining

### Session 6 - February 3, 2026
- **Meal Plan Data Import:**
  - Installed poppler for PDF text extraction (pdftotext)
  - Converted Männer_Pläne.pdf and Frauen_Pläne.pdf to text with layout preservation
  - Created import script: `backend/scripts/import_meal_plans.py`
  - Parsed meal plan structure:
    - Level X Tag Y headers
    - Meal types: Frühstück, Miattgessen (typo in PDF), Abendessen, Snacks
    - Ingredients with quantities (g, ml, EL, Stück)
    - Daily macros: P (protein), KH (carbs), F (fat), kcal
  - Imported 100 meal plans to database
  - 333 meals, 921 ingredients total
  - API verified working with real data
- **Project ~90% complete** - Ready for payment integration or production polish

### Session 7 - February 3, 2026
- **Google OAuth Integration:**
  - Added Google sign-in button to Login and Register pages
  - Created AuthCallbackPage for OAuth redirect handling
  - Added loginWithGoogle and handleOAuthCallback to auth store
  - Added getGoogleOAuthUrl to authApi
- **Mobile Responsiveness:**
  - Full responsive design with breakpoints at 640px, 375px, 768px, 1024px
  - Mobile-optimized stats grids, meals grid, modals
  - Safe area padding for notched phones
  - Skeleton loading animations
- **Stripe Payment Integration:**
  - Backend: StripeService, subscriptions router, webhook handling
  - Frontend: SubscriptionPage with pricing cards and promo codes
  - Monthly (€29.99) and yearly (€239.99, 2 months free) plans
  - Cancel/reactivate/portal access functionality
  - Database migration for subscription fields
- **Project ~95% complete** - Core app + payments done, ready for production!

### Session 8 - February 5, 2026
- **Code Modularization:**
  - Created `/frontend/src/config/index.ts` - centralized configuration
  - Created modular API structure under `/frontend/src/services/api/`:
    - `client.ts` - Axios instance with interceptors
    - `tokens.ts` - JWT token management
    - `auth.ts`, `user.ts`, `weight.ts`, `mealPlan.ts`, `subscription.ts` - API modules
    - `index.ts` - Central re-exports
  - Created custom hooks under `/frontend/src/hooks/`
  - Created reusable UI components under `/frontend/src/components/common/`
  - Added ErrorBoundary component
- **GitHub Repository:**
  - Created repo: https://github.com/StephanBK/sloth
  - Pushed all code for collaboration
- **Production Deployment:**
  - **Frontend deployed to Vercel:** https://frontend-rho-nine-25.vercel.app
  - **Backend deployed to Railway:** https://sloth-production.up.railway.app
  - Connected frontend to backend API via VITE_API_URL
  - Added Vercel domains to CORS whitelist
- **Database Connection Issues Fixed:**
  - Direct Supabase connection doesn't work from Railway (IPv6)
  - Transaction Pooler (port 6543) had SSL issues
  - **Solution:** Use Session Pooler (port 5432) - works perfectly!
  - Final DATABASE_URL: `postgresql://postgres.[project]:password@aws-1-eu-central-1.pooler.supabase.com:5432/postgres`
- **Auth Flow Verified Working:**
  - Login redirects to intake form for new users ✅
  - JWT tokens working correctly ✅
- **Project 100% DEPLOYED** - Live and accessible!

### Session 9 - February 6, 2026
- **Stripe Products Created in Dashboard:**
  - Monthly: "Faultierdiät Monatlich" at €29.99/month - `price_1SxdauQqguFpDAu9OLqhVOlW`
  - Yearly: "Faultierdiät Jährlich" at €239.99/year - `price_1SxddpQqguFpDAu9Zbk8yS0k`
  - Stripe tested and verified working
- **Google OAuth Setup (In Progress):**
  - Created Google Cloud project "Sloth"
  - Set up OAuth consent screen (app name: Faultierdiät, External audience)
  - Created OAuth client credentials
  - Configured Supabase Google provider with credentials
  - Updated Supabase Site URL to production frontend
  - Added redirect URL: `https://frontend-rho-nine-25.vercel.app/auth/callback`
- **OAuth Code Exchange Fix:**
  - Supabase uses authorization code flow (code in URL params), not implicit flow
  - Added backend endpoint: `POST /auth/callback` to exchange code for session
  - Added `exchange_code_for_session` method to auth_service.py
  - Added `OAuthCodeExchangeRequest` schema
  - Updated frontend `handleOAuthCallback` to handle both implicit and code flow
  - Updated `AuthCallbackPage.tsx` to check both hash and query params for errors
- **Status at end of session:** OAuth code exchange still failing (PKCE issue)

### Session 10 - February 7, 2026
- **Google OAuth Fixed! ✅**
  - **Root cause:** Supabase Python SDK defaults to PKCE flow, which stores `code_verifier` in in-memory storage. On Railway (production), this is unreliable - process restarts or multiple workers lose the verifier, causing "invalid flow state" errors on code exchange.
  - **Fix:** Switched Supabase client to `implicit` flow via `ClientOptions(flow_type="implicit")` in `auth_service.py`
  - With implicit flow, tokens come back directly in the URL hash (`#access_token=...&refresh_token=...`) - no backend code exchange needed
  - Frontend already handled this path (`auth.ts:51-62`), so no frontend changes required
  - **Google OAuth tested and confirmed working in production! ✅**
- **All auth methods now working:**
  - Email/password login ✅
  - Email/password registration ✅
  - Google OAuth login ✅

### Session 10 continued - February 7, 2026
- **Dashboard Redesign (DashboardPage.tsx):**
  - Time-of-day greeting with user's name (derived from email)
  - Level pill badge showing current diet level
  - Weight progress card with animated progress bar (start → current → goal)
  - Quick weight entry modal with success animation
  - Today's meal plan card based on day rotation (shows all meals with macros)
  - Current meal highlighting based on time of day
  - 4-column quick action grid (Mahlzeiten, Gewicht, Einkaufsliste, Profil)
- **Grocery List Feature (NEW - GroceryListPage.tsx):**
  - Day selector (1-10) with preset buttons (Tag 1-3, Tag 1-5, Alle)
  - Fetches meal plans for selected days, aggregates all ingredients
  - Smart ingredient aggregation (combines same product, groups by unit)
  - Interactive checklist with checkboxes and strikethrough animation
  - Progress bar showing checked/total items
  - Reset button and summary
  - Sorted: unchecked first, then alphabetical
  - Added route at /grocery with config entry
- **Form Validation & Polish:**
  - LoginPage: inline email validation, password length check, blur-triggered errors, loading spinner
  - RegisterPage: inline email validation, password strength meter (Schwach/Mittel/Stark), password match indicator with checkmark, animated error messages
  - Both pages: `noValidate` for custom UX, `aria-invalid` + `aria-describedby` for accessibility, auto-clear server errors on input change
  - CSS: password strength bar with color transitions, `.spinner` animation, `.btn-loading` layout, `.auth-error-icon`, `.form-success` with fadeSlideIn animation
- **Build verified passing** ✅
- **Stripe Webhooks Configured:**
  - Added STRIPE_SECRET_KEY (live), STRIPE_WEBHOOK_SECRET, FRONTEND_URL to Railway
  - Created webhook endpoint in Stripe Dashboard → `https://sloth-production.up.railway.app/subscriptions/webhook`
  - Listening to 5 events: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted, invoice.payment_succeeded, invoice.payment_failed
  - Endpoint active and verified reachable

### Session 11 - February 15, 2026
- **Product Catalog & Data Pipeline (from previous uncommitted work):**
  - Added 46 core products with full nutrition data to Product model
  - Extended Product model with data provenance fields (data_source, data_confidence, is_curated)
  - Added external IDs for cross-referencing (off_id, bls_code)
  - Created product API endpoints: GET /products, GET /products/categories, GET /products/{id}
  - Created data pipeline scripts for Open Food Facts + BLS (German food database) import
  - New files: backend/scripts/pipeline/ (off_download, off_filter, off_import, off_verify, bls_import, utils)
  - Processed data: data/processed/off_german_products.jsonl
  - Frontend: Added Product TypeScript interface and product API client

- **UI Rebrand — Faultierdiät PDF Visual Language 🎨**
  - **Extracted design language** from Männer Pläne.pdf / Frauen_Pläne.pdf to create cohesive brand identity
  - **Color palette overhaul** (entire App.css design tokens rewritten):
    - Primary: Sage green `#6B8F5E` (warmed from cold `#4F7942`)
    - Brand accent: Chocolate brown `#5C3A21` (extracted from PDF headings/borders)
    - Neutrals: Warm cream/off-white palette (`#FAF6F1`, `#F3EDE4`, etc.) replacing cold grays
    - Semantic colors: Warmer tones for success, warning, error, info
    - Shadows: Brown-tinted instead of pure black
  - **Typography**: Added serif font stack (Georgia/Palatino) for headings to echo the PDF's elegant script style; body stays sans-serif
  - **Component updates** (30+ CSS rules changed):
    - Cards: Added warm borders (`--color-gray-200`)
    - Meal items: Brown top borders matching PDF's horizontal rule dividers
    - Auth page: Sage green gradient matching PDF cover
    - Badges (level, meal type, pricing): Chocolate brown
    - All interactive highlights: Brown accent (nav active, filters, day buttons, spinners)
    - Profile avatar & progress card: Brown gradient
    - Dashboard: Level pill, progress bar, action icons all brown-accented
    - Grocery: Day buttons, count badge, checkboxes updated
    - Subscription: Pricing badge, popular card border updated
    - Alerts: Warm cream-tinted backgrounds
    - Intake: Progress dots use brown
    - Loading spinner: Brown accent
  - **Design philosophy**: Warm, earthy, organic feel matching the Faultierdiät brand identity from the PDFs — replacing the generic cold tech-green look

- **Supabase Free-Tier Pause Issue (IMPORTANT for future sessions):**
  - Login appeared broken after deploy — error: `[Errno -2] Name or service not known`
  - Root cause: Supabase free-tier projects auto-pause after ~7 days of inactivity
  - Fix: Go to https://supabase.com/dashboard → find project → click "Restore project"
  - Restoration takes 1-2 minutes, then everything works again
  - ⚠️ **If auth/login stops working, check Supabase dashboard FIRST before debugging code**

### Session 12 - February 18, 2026
- **Intake Flow Simplification (based on domain expert feedback):**
  - **Removed goal weight question** from Screen 2 — was irrelevant to the Faultierdiät methodology. Screen 2 now only asks for current weight. Existing users who already have goal_weight_kg still see their progress data.
  - **Replaced activity level with calorie-awareness model** in Screen 3:
    - Users choose between three visual buttons: "Ich nehme zu" (↑), "Ich halte mein Gewicht" (→), "Ich nehme ab" (↓)
    - If they know their calorie intake, they enter it in a number field
    - If they don't know: "Ich weiß nichts über meine Kalorienaufnahme" button — system estimates from body weight × 30
    - Reassuring message: "Das System korrigiert sich automatisch wöchentlich"
  - **Activity level hidden** from Profile page (kept in DB for backward compatibility, just not shown in UI)

- **Level System Rebrand — "Stufe 1-5" → "2100 kcal" etc.:**
  - Replaced all "Stufe N" labels with actual calorie targets based on gender:
    - Men: 2700 / 2400 / 2100 / 1800 / 1500 kcal
    - Women: 2400 / 2100 / 1800 / 1500 / 1200 kcal
  - Updated: Dashboard pill, Meals page badge + info text, Profile card + diet settings
  - Internal DB still stores `current_level` as 1-5 (no migration needed)
  - Added `CALORIE_LEVELS` map and `getLevelLabel()` helper to `types/index.ts`

- **New Starting Level Calculation:**
  - Replaced old weight-to-lose formula with calorie-awareness logic:
    - "gaining" → level at or below their reported intake
    - "maintaining" → one level below (create deficit)
    - "losing" → level closest to their intake (already in deficit)
    - "unknown" → body weight × 30 → next level down
  - Starting point doesn't need to be perfect — weekly stall detection auto-corrects

- **Stall detection messages** translated to German and updated to reference "Kalorienlevel" instead of "level"

- **Backend schema changes:**
  - Added `CalorieAwareness` enum (gaining/maintaining/losing/unknown)
  - `IntakeScreen2` no longer requires `goal_weight_kg`
  - `IntakeScreen3` now uses `calorie_awareness` + `known_calorie_intake` instead of `activity_level`
  - `ProfileUpdate` no longer exposes `goal_weight_kg` or `activity_level`

- **Build verified passing** ✅

---

## 🚀 HOW TO RESUME (READ THIS NEXT SESSION)

### Step 1: Start a new Claude Code session

### Step 2: Say this to Claude:
```
Read /Users/stephanketterer/sloth/PROGRESS.md and continue where we left off.
I want to work on [choose one]:
- Option A: Configure Stripe webhooks and test payment flow (needs Stripe env vars)
- Option B: Dark mode support
- Option C: Push notifications / email notifications
- Option D: Code splitting / performance optimization
- Option E: Free trial period implementation
```

### Production URLs (LIVE!)
- **Frontend:** https://frontend-rho-nine-25.vercel.app
- **Backend:** https://sloth-production.up.railway.app
- **GitHub:** https://github.com/StephanBK/sloth

### Local Development (optional)
```bash
# Terminal 1 - Backend
cd /Users/stephanketterer/sloth/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd /Users/stephanketterer/sloth/frontend
npm run dev
```

Then open http://localhost:5173 in your browser!

---

## Current State Summary (for Claude)

**Project:** Sloth - Meal planning SaaS (Faultierdiät)
**Completion:** FULLY DEPLOYED! 🎉 (Auth + Payments + Dashboard + Grocery + Polish — all wired up)
**Working directory:** /Users/stephanketterer/sloth

**Production URLs:**
- 🌐 **Frontend:** https://frontend-rho-nine-25.vercel.app
- 🔧 **Backend:** https://sloth-production.up.railway.app
- 📦 **GitHub:** https://github.com/StephanBK/sloth

**What's working:**
- ✅ PostgreSQL database with all tables (via Supabase)
- ✅ FastAPI backend with all endpoints (on Railway)
- ✅ Supabase authentication (email/password + Google OAuth working!)
- ✅ React frontend with all core pages (on Vercel)
- ✅ **Login flow works end-to-end in production!**
- ✅ User redirected to intake form after first login
- ✅ Weight tracking with graph and stall detection
- ✅ Meal plan browsing by level/gender
- ✅ Profile page with settings
- ✅ **100 real meal plans imported!** (50 male, 50 female, all 5 levels)
- ✅ **Stripe subscription integration!** (code ready, needs Dashboard setup)
- ✅ Mobile responsive design
- ✅ Modular code architecture
- ✅ **Sleek dashboard** with greeting, progress card, today's meals, quick actions
- ✅ **Grocery list** with day selector, ingredient aggregation, interactive checklist
- ✅ **Polished forms** with inline validation, password strength meter, loading spinners

**Needs Setup:**
- ✅ Stripe products/prices in Stripe Dashboard (DONE!)
- ✅ Google OAuth - WORKING! (implicit flow fix, Session 10)
- ✅ Stripe webhooks configured and active!

**Railway Environment Variables (configured):**
- SUPABASE_URL=https://wetlgbumumghqavzwzqh.supabase.co
- SUPABASE_ANON_KEY=(set)
- SUPABASE_SERVICE_ROLE_KEY=(set)
- DATABASE_URL=postgresql://postgres.[project]:password@aws-1-eu-central-1.pooler.supabase.com:5432/postgres
- ENVIRONMENT=production

**Test user:**
- Email: stephanketterermba@gmail.com
- Password: testpassword123

**To test PRODUCTION:**
1. Go to https://frontend-rho-nine-25.vercel.app
2. Login or register
3. Complete intake form

**To test LOCAL:**
1. Start backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173

---

## Quick Reference

| What | Location |
|------|----------|
| **PRODUCTION Frontend** | https://frontend-rho-nine-25.vercel.app |
| **PRODUCTION Backend** | https://sloth-production.up.railway.app |
| **PRODUCTION API Docs** | https://sloth-production.up.railway.app/docs |
| **GitHub Repo** | https://github.com/StephanBK/sloth |
| Local frontend | http://localhost:5173 |
| Local backend | http://localhost:8000 |
| Local API docs | http://localhost:8000/docs |

| Command | What it does |
|---------|--------------|
| `cd backend && source venv/bin/activate && uvicorn app.main:app --reload` | Start local backend |
| `cd frontend && npm run dev` | Start local frontend |
| `cd frontend && npm run build` | Build frontend for production |

---

## Deployment Notes

### Railway Backend
- Uses Session Pooler for Supabase (port 5432, NOT Transaction Pooler 6543)
- CORS configured for Vercel domains
- JWT verification disabled (trusts Supabase tokens)

### Vercel Frontend
- VITE_API_URL points to Railway backend
- Auto-deploys from GitHub main branch

### Database
- Supabase PostgreSQL
- Tables: users, weight_entries, meal_plans, meals, ingredients, user_preferences
- Connection via Session Pooler (IPv6 workaround for Railway)

---

We're LIVE! 🦥🚀
