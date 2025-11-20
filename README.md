# Yorkie Bakery — AI-Enhanced Web App

## 🐶 Overview
Yorkie Bakery is a full-stack AI-powered bakery application featuring menu browsing, ordering, music streaming, image-based recommendations, and a full RAG-powered chat assistant.

## ✨ Features

### Admin (Oscar)
- Admin dashboard
- CRUD menu management (with images)
- Upload music tracks
- Manage campaigns/events
- Moderate reviews
- Receive new order alerts

### Regular Users
- Register/login with email verification
- Browse menu (20–100 items pagination)
- Add to cart & checkout
- Leave reviews & preferences
- Subscribe to events/notifications
- Chat-based AI assistant “Oscar”
- Image recognition (OpenAI Vision)

---

## 🧱 Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React (AI Demo), HTMX/Jinja2 |
| Backend | FastAPI |
| Database | PostgreSQL |
| Storage | AWS S3 |
| AI / LLM | OpenAI GPT + Vision |
| Vector DB | ChromaDB |
| Deployment | Docker + EC2 |

---

## 🤖 AI Architecture

### Hybrid RAG Pipeline
```
User Query/Image
     ↓
OpenAI → Extract filters
     ↓
Vector Search (ChromaDB) Top-50
     ↓
Strict Backend Filters
     ↓
Rank + Final Recommendations
```

### Vision Image Flow
```
Image Upload
 → OpenAI Vision
 → Flavor/Tag Extraction
 → Vector Search
 → Recommended Items
```

---

## 🏗️ System Architecture

```
                React + Vite (AI Demo)
                        │
                        ▼
                  FastAPI Backend
     ┌─────────────┬───────────┬──────────────┬─────────┐
     ▼             ▼           ▼              ▼         ▼
PostgreSQL     ChromaDB     OpenAI        AWS S3    AWS SES
 Menu DB       Vectors    GPT/Vision    Images/Music Email
```

---

## 🗄️ Database Schema

### PostgreSQL Tables
- `user_account`
- `menu_item`
- `music_track`
- `orders`
- `order_items`

### ChromaDB Embeddings
```
{ id, title, tags[], flavor_profiles[], embedding_vector[] }
```

---

## 🚀 API Reference

### 🔐 Authentication API
```
POST /auth/register_form
POST /auth/login_form
POST /auth/resend_verification
POST /auth/forgot_password
POST /auth/reset_password
GET  /auth/login/google
GET  /auth/login/google/callback
```

### 🍽 Menu API
```
GET  /menu/view
GET  /menu/{id}
POST /menu/new
POST /menu/update/{id}
POST /menu/delete/{id}
```

### 🛒 Cart & Orders API
```
GET  /cart/view
POST /cart/add
POST /cart/remove/{id}
POST /cart/checkout
```

### 🤖 AI API
```
POST /ai/demo
POST /ai/chat
POST /ai/vision
GET  /ai/debug
```

---

## 🌐 Deployment

- Docker Compose
- PostgreSQL + ChromaDB containers
- Deployed on **AWS EC2**
- Domains:
  - https://yorkiebakery.com
  - https://beta.yorkiebakery.com
- S3 (images/music)
- SES (emails + password reset)

---

## 📘 System Design Page
Visit:
```
/system-design
```
Contains diagrams, HLD, and architecture explanations.

---

## 🧭 Future Enhancements
- Personalized user taste model
- Collaborative filtering
- Voice ordering (Whisper)
- Admin analytics dashboard
- Advanced ranking model

---

## ❤️ About
A showcase project combining:
- Modern backend engineering  
- AI/RAG techniques  
- Practical product design  

**Where bakery meets intelligence 🐾🥐✨**
