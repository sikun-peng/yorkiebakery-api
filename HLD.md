# 🐶 Yorkie Bakery — AI-Enhanced Web App

Yorkie Bakery is a full-stack web application for bakery menu browsing, ordering, event campaigns, and an AI-powered chat assistant that helps users discover what to order. The system supports two roles: **Admin (Oscar)** and **Regular Users**, and includes a recommendation & RAG-based chat experience.

---

## ✨ Features

### Admin (Oscar)
- Full admin dashboard
- Add / update / delete menu items (with images)
- Manage events + seasonal campaigns
- Moderate reviews and comments
- Upload music tracks for bakery ambiance
- Receive notifications for new orders

### Regular Users
- Create an account & login
- Browse menu with pagination (20–100 items)
- Place orders & reservations
- Leave reviews & set taste preferences
- Subscribe to offers / events
- Semantic search across menu & music
- **Chat with Oscar** for recommendations & help

---

## 🧱 Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React (User UI), HTMX/Jinja2 (Admin Dashboard) |
| Backend | **FastAPI** (Python) |
| Database | **PostgreSQL** |
| Storage | AWS S3 (images + music) |
| AI | OpenAI GPT + **LangChain RAG** |
| Vector Search | **FAISS** |
| Auth | JWT + Role-based Access Control |
| Deployment | Docker → EC2 / ECS / GCP / Fly.io |

---

## 🧠 AI Architecture (RAG)

Yorkie uses **Retrieval-Augmented Generation** to give grounded, accurate, friendly answers.

User → Chat UI → /chat API → Embedding → Vector Search (FAISS)
↓
Retrieve Top Matching Menu Items
↓
Construct Yorkie Personality Prompt → GPT Response
↓
UI displays reply

- Prevents hallucination
- Makes Yorkie *actually know the menu*
- Allows natural questions like:
  > *“I want something fluffy and sweet.”*

---

## 🗄️ System Architecture

┌────────────────────── UI ──────────────────────┐
| React User App        | Admin Dashboard (HTMX) |
└─────────────┬─────────┴───────────┬────────────┘
│                     │
▼                     ▼
┌──────────────────────────────────┐
│           FastAPI API            │
│ (Auth, Menu, Orders, Chat, etc.) │
└─────────────────┬────────────────┘
│
┌─────────────────────────────┐
│     Core Infrastructure     │
│   PostgreSQL (main data)    │
│   S3 (images/music)         │
│   FAISS (vector index)      │
│   OpenAI (LLM + embeddings) │
└─────────────────────────────┘

---

## 🗃️ Data Model (Simplified)

User(id, email, password_hash, role, preferences)
MenuItem(id, title, description, tags[], image_url, is_available)
Order(id, user_id, items[], total_price, status)
Review(id, user_id, menu_item_id, rating, text)
Campaign(id, name, description, image, start_date, end_date)
Music(id, title, audio_url)

---

## 🚀 Milestone Plan

| # | Milestone | Outcome |
|---|---|---|
| M1 | Auth & Roles | Users + Admin login |
| M2 | Menu CRUD + Images | Admin menu mgmt + pagination |
| M3 | Orders & Alerts | Order workflow + notifications |
| M4 | Reviews + Preferences | Flavor profile + social reviews |
| M5 | Search & Campaigns | Keyword + tag + semantic search |
| **M6** | **AI Recommender + RAG Chat** | FAISS vector search + GPT chat |
| M7 | Music Uploads | Admin ambient music |
| M8 | Admin Dashboard | Full bakery operations UI |
| M9 | Deployment | Cloud hosting + HTTPS |
| M10 | Polish | Logging, UX, QA |

---

## 🧭 Roadmap / Future Extensions
- Yorkie ordering assistant ("Place this order for me")
- Seasonal recommendation tuning
- Voice chat (WebRTC + Whisper)
- Loyalty rewards & referral perks

---

## 🐾 Personality Prompt (Yorkie Mode)

Yorkie speaks in:
- Warm, cute bakery tone
- Encouraging language
- Never robotic

Example:
> “WOOF! 🐾 I sniffed out the perfect bun for you.  
> It’s fluffy, sweet, and full of love! 🍞💗 Want me to fetch it for your cart?”

---

## ❤️ About This Project
This project is being built to learn:
- Real-world backend engineering patterns
- AI + RAG integration
- Scalable product system design
- UI/UX for consumer-facing web apps

Where Bakery Meets Intelligence ✨🐶🥐

APIs
http://localhost:8000/auth/login/google