# SLOTH - Project Specification & Technical Documentation

**Last Updated:** January 31, 2026  
**Status:** Pre-Development Planning Phase

---

## 1. PROJECT OVERVIEW

### What is Sloth?
A mobile-first SaaS web application that converts your brother's successful Excel-based diet system ("Faultierdiät") into an intelligent, interactive platform.

### Current State
- **Brother's Product:** Static PDF + Google Sheets package
- **Price:** ~$100 one-time purchase (gender-specific)
- **Sales:** ~200 customers, ~$20K/month revenue
- **Problem:** Mobile experience is terrible, no intelligence, manual product maintenance

### Target Market
- **Geography:** Germany (initially)
- **Audience:** Health-conscious, fitness-focused individuals
- **Age:** Younger demographic (18-40)
- **Tech Literacy:** Varies - app must be extremely simple
- **Device:** Mobile-first (critical requirement)

---

## 2. BUSINESS MODEL

### Pricing
- **$29.99/month** subscription
- Gender-agnostic (both plans included)
- Germany-only initially

### Revenue Projection
- Current: 200 one-time customers
- Target Year 1: 500-1,000 subscribers
- Target Year 2: 5,000-10,000 subscribers
- Long-term: 10K-100K users possible

### Development Language vs Deployment
- **Develop:** English (code, admin panel)
- **Deploy:** German (user-facing)

---

## 3. THE FAULTIERDIÄT SYSTEM (Core Logic)

### 3.1 System Philosophy
- **Design Goal:** Fat loss with minimum cognitive load
- **Core Concept:** Users don't manage calories - they follow pre-built deterministic plans
- **Key Innovation:** Zero decision fatigue, maximum compliance

### 3.2 Level System (Global Logic)

**5 Levels = 5 Fixed Calorie Targets**

| Group | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|-------|---------|---------|---------|---------|---------|
| Men | ~2700 kcal | ~2400 kcal | ~2100 kcal | ~1800 kcal | ~1500 kcal |
| Women | ~2400 kcal | ~2100 kcal | ~1800 kcal | ~1500 kcal | ~1200 kcal |

**Progression Rules:**
- Drop levels ONLY when weight stalls (2+ weeks no progress)
- Level 5 maximum duration: 2-3 weeks (hard stop)
- Never increase cardio when dropping levels (breaks calorie signal)

### 3.3 Meal Plan Structure

**Current Content:**
- 50 meal plans for men (5 levels × 10 days each)
- 50 meal plans for women (5 levels × 10 days each)
- **100 total pre-built days**

**Each Day Plan Contains:**
```
Level X - Day Y
├── Breakfast
├── Lunch
├── Dinner
├── Snacks
└── Daily Totals
    ├── Protein (P)
    ├── Carbs (KH)
    ├── Fat (F)
    └── kcal
```

### 3.4 Meal Entry Data Model

Each meal specifies:
- Exact product name (currently REWE-branded, but we're not limiting to REWE)
- Exact quantity (grams, units, packages)
- Preparation method (usually "1 EL Olivenöl oder Butterschmalz")
- Implicit macros (shown per meal/day, not per ingredient)

**Example:**
```
400g Chicken Minutenschnitzel
125g Ben's Original Rice
300g Broccoli
1 EL Olivenöl
```

### 3.5 Flexibility Rules

**ALLOWED:**
- Swap meal order
- Skip snacks
- Split meals
- Eat same day repeatedly all week
- Batch cooking
- Add consistent extra calories daily (systematic deviation)

**NOT ENCOURAGED (but allowed):**
- Product substitution (manual effort)
- Different supermarkets
- High-calorie density swaps

**CRITICAL INVARIANT:**
> Total daily calories must remain consistent

### 3.6 "Systematic Deviation" Concept

**Key Idea:** If you add the same extra calories EVERY day (e.g., coffee with milk, daily protein bar), the system still works because:
- Absolute calories shift
- Relative deficit remains stable
- No daily tracking needed
- Zero guilt

### 3.7 Supporting Tools (Current Excel System)

**Faultierrechner (Calculator):**
- Calculates maintenance calories
- Determines starting level
- Signals when to drop levels

**Einkaufshelfer (Shopping Helper):**
- Aggregates shopping lists across multiple days
- Reduces planning friction

**Current Implementation:** Google Sheets (bookkeeping, not interactive)

---

## 4. FEATURE REQUIREMENTS

### 4.1 ESSENTIAL (MVP - Must Have)

#### Mobile-First Experience
- PWA (Progressive Web App) - installs like native
- Touch-optimized interface
- Offline capability for meal plans
- Fast load times

#### User Account System
- Email/password registration
- Password reset
- Profile management
- Data privacy (GDPR compliant)

#### Meal Plan Database & Navigation
- Browse 100 pre-built days (expandable)
- Filter by level, gender, day number
- Mark days as "favorite" or "disliked"
- View full day details (all meals + macros)

#### User Preference Learning
- Track which days user dislikes
- Auto-hide disliked days from suggestions
- Learn favorite days over time
- Simple thumbs up/down interface

#### Progress Tracking - Weight
- Daily weight entry
- Weight graph (show trend over time)
- Level transition tracking
- Stall detection (auto-suggest level drop after 2 weeks)

#### Grocery List Generation
- Select multiple days for week
- Aggregate ingredients across days
- Export as PDF
- Group by category (produce, meat, dairy, etc.)

### 4.2 IMPORTANT (v1.0 - Post-MVP)

#### Smart Product Substitutions
- LLM-powered suggestions when product unavailable
- Maintain calorie/macro equivalence
- Store-agnostic alternatives
- User can accept/reject suggestions

#### Recipe Modifications
- LLM-powered adjustments within calorie constraints
- "Make this vegetarian"
- "Swap chicken for fish"
- "I don't like broccoli"
- Recalculate macros automatically

#### Advanced Filters
- Dietary preferences (vegetarian, pescatarian, etc.)
- Allergen exclusions
- Ingredient dislikes
- Preparation time

#### Meal Plan Customization
- Reorder meals within day
- Skip/replace individual meals
- Duplicate favorite days
- Create custom weeks

### 4.3 DEFERRED (Future Versions)

- Progress photos upload
- Fitness tracker integration
- Barcode scanning
- Social/community features
- Automatic grocery delivery integration (when APIs available)
- AI meal plan generation (beyond 100 pre-built)

---

## 5. TECHNICAL ARCHITECTURE

### 5.1 Tech Stack

**Backend:**
- **Language:** Python
- **Framework:** FastAPI
- **Why:** Modern, fast, auto-generated API docs, easier learning curve than Django

**Frontend:**
- **Framework:** React + Vite
- **Build Target:** Progressive Web App (PWA)
- **Why:** One codebase for mobile/tablet/desktop, installable like native app

**Database:**
- **Primary:** PostgreSQL
- **Why:** Stephan has experience, robust, handles complex queries, free tier available

**Authentication:**
- **Service:** Supabase Auth
- **Why:** Free tier, handles all security, battle-tested, easy integration

**Hosting:**
- **Platform:** Railway.app
- **Cost:** $5/month → scales to $50-200 as users grow
- **Why:** Simple deployment, PostgreSQL included, affordable scaling

**LLM Integration:**
- **Provider:** Claude API (Anthropic)
- **Use Cases:** Product substitutions, recipe modifications
- **Cost Control:** Rate limiting, caching, user quotas

### 5.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    USER DEVICES                          │
│  (Phone, Tablet, Desktop - via PWA)                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              REACT PWA (Frontend)                        │
│  - React Router (navigation)                             │
│  - Service Worker (offline)                              │
│  - IndexedDB (local cache)                               │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│           FASTAPI BACKEND (Python)                       │
│  ├── Auth Middleware (Supabase)                          │
│  ├── API Routes                                          │
│  │   ├── /users                                          │
│  │   ├── /meal-plans                                     │
│  │   ├── /grocery-lists                                  │
│  │   ├── /progress                                       │
│  │   └── /preferences                                    │
│  ├── Business Logic                                      │
│  └── LLM Integration (Claude API)                        │
└────────────────────┬────────────────────────────────────┘
                     │ SQL
                     ▼
┌─────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                         │
│  ├── users                                               │
│  ├── meal_plans                                          │
│  ├── ingredients                                         │
│  ├── user_preferences                                    │
│  ├── weight_entries                                      │
│  └── grocery_lists                                       │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Database Schema (Preliminary)

**Core Tables:**

```sql
-- Users
users
  - id (uuid, PK)
  - email (unique)
  - gender (enum: male, female)
  - current_level (1-5)
  - created_at
  - updated_at

-- Meal Plans
meal_plans
  - id (uuid, PK)
  - level (1-5)
  - day_number (1-10)
  - gender (enum: male, female)
  - total_kcal
  - total_protein
  - total_carbs
  - total_fat
  - created_at
  - updated_at

-- Meals (within a plan)
meals
  - id (uuid, PK)
  - meal_plan_id (FK)
  - meal_type (enum: breakfast, lunch, dinner, snack)
  - order_index
  - instructions

-- Ingredients (for a meal)
ingredients
  - id (uuid, PK)
  - meal_id (FK)
  - product_name
  - quantity
  - unit
  - kcal
  - protein
  - carbs
  - fat

-- User Preferences
user_preferences
  - id (uuid, PK)
  - user_id (FK)
  - meal_plan_id (FK)
  - preference (enum: liked, disliked, neutral)
  - created_at

-- Weight Tracking
weight_entries
  - id (uuid, PK)
  - user_id (FK)
  - weight_kg
  - measured_at
  - created_at

-- Grocery Lists
grocery_lists
  - id (uuid, PK)
  - user_id (FK)
  - week_start_date
  - created_at

grocery_list_items
  - id (uuid, PK)
  - grocery_list_id (FK)
  - ingredient_id (FK)
  - quantity
  - checked (boolean)
```

### 5.4 Admin Panel (for Brother)

**Required Functionality:**
- Add/edit/delete meal plans
- Manage ingredients within meals
- Update product names when SKUs change
- View user statistics (anonymized)
- Bulk import/export (CSV/JSON)

**Technical Approach:**
- Separate admin routes in FastAPI
- Simple React admin UI (basic CRUD forms)
- Role-based access control
- Brother learns basic web forms (WYSIWYG not needed initially)

---

## 6. COST PROJECTIONS

### 6.1 Pre-Revenue (Months 1-3)
- Railway.app: $5/month
- Domain: $15/year (~$1.25/month)
- Supabase Auth: Free tier
- Claude API: $0 (minimal testing)
- **Total: ~$6-10/month**

### 6.2 Early Users (100-500 users)
- Railway.app: $20-50/month
- Claude API: ~$30-50/month (rate limited)
- **Total: $50-100/month**
- **Revenue at 100 users:** $2,999/month
- **Net: +$2,900/month**

### 6.3 Scale (10,000 users)
- Railway.app: $200-500/month
- Claude API: ~$150/month (optimized, cached)
- CDN/Storage: $50/month
- **Total: ~$400-700/month**
- **Revenue at 10K users:** $299,900/month
- **Net: +$299,200/month**

**LLM Cost Calculation:**
- 10K users × 5 LLM queries/month = 50K calls
- 50K × $0.003/call = $150/month
- As % of revenue: 0.05% (negligible)

---

## 7. DEVELOPMENT TIMELINE

### Assumptions
- Daily work: 2-3 hours
- Claude Code assistance throughout
- Stephan has "some Python" + PostgreSQL experience
- Learning React from scratch

### Week-by-Week Plan

**Weeks 1-2: Backend Foundation**
- FastAPI project setup
- PostgreSQL schema creation
- Basic CRUD APIs for meal plans
- Authentication integration (Supabase)
- **Learning:** FastAPI basics, API design patterns

**Weeks 3-5: Frontend Foundation**
- React + Vite project setup
- PWA configuration
- Basic routing (React Router)
- Connect to backend API
- Authentication flow (login/register)
- **Learning:** React fundamentals, component architecture, state management

**Weeks 6-8: Core Features**
- Meal plan browsing UI
- Filter/search functionality
- User preference system (like/dislike)
- Grocery list generation
- PDF export
- **Learning:** Complex state, API integration, UI/UX patterns

**Weeks 9-10: Progress Tracking**
- Weight entry form
- Weight graph visualization
- Level transition logic
- Stall detection algorithm
- **Learning:** Chart libraries, date handling, algorithms

**Weeks 11-12: Polish & Testing**
- Mobile optimization
- Offline functionality
- Performance optimization
- User testing with brother's customers
- Bug fixes
- **Learning:** PWA service workers, performance profiling

**Week 13: Launch Prep**
- Deployment to Railway
- Domain setup
- SSL certificate
- Admin panel for brother
- Data migration (100 meal plans)

**TARGET MVP LAUNCH: 12-13 weeks (3 months)**

---

## 8. LEARNING RESOURCES

### FastAPI
- **Official Docs:** https://fastapi.tiangolo.com/tutorial/
- **Course:** "FastAPI - The Complete Course" (Udemy)
- **Time:** 1-2 weeks to basics

### React
- **Official Docs:** https://react.dev/learn
- **Course:** "React - The Complete Guide" (Udemy)
- **Time:** 3-4 weeks to proficiency

### PWA
- **Guide:** "Your First Progressive Web App" (Google)
- **Docs:** https://web.dev/progressive-web-apps/
- **Time:** 1 week to understand

### PostgreSQL
- Already have experience ✓
- Refresh: "PostgreSQL Tutorial" (postgresqltutorial.com)

---

## 9. CRITICAL SUCCESS FACTORS

### What Makes This Work

1. **Daily Commitment**
   - 2-3 hours every single day
   - No multi-week gaps
   - Consistency > intensity

2. **Claude Code Partnership**
   - Ask questions immediately when stuck
   - Iterate quickly
   - Learn by building, not just reading

3. **MVP Discipline**
   - Ship basic version in 12 weeks
   - Add features after revenue
   - Don't gold-plate

4. **Brother's Involvement**
   - Weekly check-ins
   - Test every feature
   - Provide customer feedback

5. **Mobile-First Obsession**
   - Test on phone constantly
   - Touch targets large enough
   - Fast load times

---

## 10. RISK MITIGATION

### Technical Risks

**Risk:** React learning curve too steep  
**Mitigation:** Use simple state management initially, no Redux until needed

**Risk:** PWA complexity  
**Mitigation:** Start web-only, add PWA features incrementally

**Risk:** Railway.app limitations at scale  
**Mitigation:** Architecture allows migration to AWS/GCP later

**Risk:** Claude API rate limits  
**Mitigation:** Implement aggressive caching, user quotas

### Business Risks

**Risk:** Brother's customers don't convert to subscription  
**Mitigation:** Offer migration discount, grandfathered pricing

**Risk:** Meal plan copyright issues  
**Mitigation:** Confirm ownership before launch (ACTION ITEM)

**Risk:** Competitor launches similar product  
**Mitigation:** Speed to market, superior mobile UX

---

## 11. OPEN QUESTIONS / ACTION ITEMS

### Legal/Business
- [ ] **URGENT:** Confirm brother owns meal plan content (copyright)
- [ ] Determine if Faultierdiät brand/name is trademarked
- [ ] GDPR compliance checklist for Germany
- [ ] Terms of service + privacy policy drafting

### Technical
- [ ] Confirm Claude Code Desktop installed and working
- [ ] Set up development environment (Python, Node.js, PostgreSQL)
- [ ] Create GitHub repository
- [ ] Railway.app account setup

### Content
- [ ] Export 100 meal plans to structured format (JSON/CSV)
- [ ] Determine product update frequency/process
- [ ] Identify most common customer support questions

### Design
- [ ] Choose color scheme / branding
- [ ] Design mobile mockups (Figma optional)
- [ ] Create logo (or defer)

---

## 12. SUCCESS METRICS

### Phase 1: MVP Launch (Month 3)
- [ ] 100 meal plans imported and functional
- [ ] 10 beta users testing
- [ ] <3 second mobile page load
- [ ] Zero critical bugs

### Phase 2: First Revenue (Month 6)
- [ ] 50 paying subscribers
- [ ] <5% churn rate
- [ ] Brother can manage content independently
- [ ] 90%+ mobile traffic

### Phase 3: Product-Market Fit (Month 12)
- [ ] 500+ paying subscribers
- [ ] Net Promoter Score >40
- [ ] <10% support tickets repeat issues
- [ ] LLM features used by >30% of users

### Phase 4: Scale (Month 24)
- [ ] 5,000+ paying subscribers
- [ ] Profitable without external funding
- [ ] Expansion to 2-3 additional markets
- [ ] Team of 2-3 people

---

## 13. NEXT IMMEDIATE STEPS

**TODAY:**
1. Confirm Claude Code Desktop ready
2. Verify brother owns meal plan content
3. Set up development environment

**THIS WEEK:**
1. FastAPI tutorial (3-4 hours)
2. Create project repository structure
3. Initialize FastAPI backend skeleton
4. Set up PostgreSQL locally

**NEXT WEEK:**
1. Design database schema in detail
2. Build first API endpoint (GET /meal-plans)
3. Import first 10 meal plans to database
4. Test API with Postman/curl

---

## FINAL NOTES

This is NOT just replicating the Excel. This is building:

✅ A living, intelligent system  
✅ That learns user preferences  
✅ With mobile-first UX  
✅ That scales to 100K users  
✅ While preserving the zero-decision-fatigue philosophy  

The methodology stays. The execution gets 10x better.

**Let's build this.**
