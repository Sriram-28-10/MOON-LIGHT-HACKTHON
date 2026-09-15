# 🌿🍲 ZeroWaste Connect - Food Surplus Management & Redistribution Platform

> A full-stack, AI-powered platform connecting canteens, restaurants, hostels, and event organizers with shelters, food banks, and local **Goat & Cow Huts** for organic non-recyclable feed redirection.

---

## 🎯 Key Features

### 🏢 Provider Registration & Profile
- Canteens, restaurants, college hostels, and event halls register with location details and organization type.

### 🍱 Post Surplus Food & Organic Scrap
- Food providers list surplus food with quantity (kg), category (cooked meals, bakery, fresh produce, organic scrap), pickup window, condition, and location.

### 🔍 Browse, Filter & Claim Catalog
- Recipients (NGOs, shelters, individuals) search and filter food by human edible vs animal feed.
- One-click claim flow generates a 6-digit OTP and dispatches automated SMS alerts.

### 🐄 Extra Feature: Animal Feed Alerts Engine
- Non-edible or near-expiry organic waste (peels, husk, trimmings) is automatically tagged for nearby **Goat & Cow Shelters**.
- Instant automated SMS alerts dispatched to partner phone numbers.

### 📊 Analytics & Visualizations
- Interactive Recharts graphics showing **Surplus vs Utilized Food (kg)**, **CO2 Emissions Saved**, Category Pie Charts, and **Provider Hero Leaderboards**.

### 🤖 AI Engine & Smart Matching
- **7-Day Demand Forecasting**: Machine Learning model predicting upcoming regional demand spikes.
- **Urgency Prioritization Score**: Dynamic score (0.0 to 1.0) based on decay time, food type, and batch size.
- **Smart Recipient Matcher**: GPS proximity & capacity match algorithm linking surplus posts to the nearest optimal recipient or animal hut.

### 🎨 3D Visuals & Animations (Three.js)
- **Intro 3D Scene**: Interactive particle transformation where food waste particles assemble into a shiny meal plate.
- **Opening 3D Network**: Dynamic node canvas showing real-time surplus food flowing from providers to shelters and animal huts.
- **Interactive 3D Cards**: Smooth mouse & touch tilt perspective effects on listing cards.
- **Closing 3D Logo**: Glowing Mobius recycle loop animation.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14+ (App Router), React, Three.js, `@react-three/fiber`, Tailwind CSS, Lucide React, Recharts
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy ORM, Pydantic, NumPy, Pandas, Scikit-learn
- **Database**: PostgreSQL (Production) / SQLite (Embedded for instant zero-dependency local dev)
- **SMS & Messaging**: Twilio REST API integration + Built-in Dev SMS Simulator Feed
- **Deployment**: Docker, Docker Compose, Kubernetes manifests (`deployments`, `services`, `ingress`, `configmap`)

---

## 🚀 Getting Started

### 1. Local Development (Backend)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 2. Local Development (Frontend)

```bash
cd frontend
npm install
npm run dev
```
- Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🐳 Docker Deployment

To launch the complete platform (Frontend + FastAPI + PostgreSQL) in containers:

```bash
docker-compose up --build -d
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## ☸️ Kubernetes Deployment

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## 🧪 Automated Testing

To run backend API unit tests:

```bash
cd backend
python test_api.py
```
