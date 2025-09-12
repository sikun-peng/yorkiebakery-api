AI-Enhanced Bakery Web App Project

⸻

Functional Requirements

1. Admin (Oscar)
	•	Can access all user profiles
	•	Can add/update/delete menu items (each with images)
	•	Can delete reviews/comments
	•	Receives alerts for new comments or orders
	•	Can create and manage campaigns for events/parties
	•	Can upload music and update titles
	•	Has full-featured admin UI

2. Regular Users
	•	Can create an account and log in
	•	Can set and update food preferences
	•	Can browse menu and music with pagination (20 or 100 per page)
	•	Can place orders and make reservations
	•	Can leave reviews on dishes
	•	Can subscribe to offers/events/campaigns
	•	Can search menu and music
	•	Can receive personalized food recommendations
	•	Can interact with chatbox assistant for tasks (e.g., check order status)

⸻

Non-Functional Requirements
	•	Responsive UI (mobile/tablet/desktop)
	•	Secure authentication (JWT-based)
	•	Role-based access control (admin vs user)
	•	Scalable backend using FastAPI + PostgreSQL
	•	Image/music upload with media serving (S3 or local storage)
	•	AI-based recommendations (OpenAI)
	•	RAG-based search assistant (OpenAI + ChromaDB/FAISS)
	•	Dockerized deployment
	•	Cloud hosting (EC2 or GCP)
	•	Monitoring/logging (optional: Prometheus, Grafana, Loki)
	•	Optional CI/CD using GitHub Actions

⸻

Project Milestone Plan

Milestone	Title	Description	Est. Time
M0	Scaffold Project	Initialize GitHub repo, Dockerize FastAPI, base folder structure	0.5 day
M1	Core API & Auth	User signup/login with JWT, admin roles	1 day
M2	Menu + Pagination	CRUD for menu items with image upload + paginated API	1–1.5 days
M3	Orders + Reservations	User order flow, reservation API, admin alert	1 day
M4	Reviews + Preferences	Review system, user preferences, moderation	1 day
M5	Search & Subscribe	Menu/music search, subscribe to campaigns	1 day
M6	AI: Recommender + RAG Chat	Personalized recommendation + OpenAI-powered chat	2 days
M7	Media Uploads	Admin upload music/images, serve via endpoint	0.5–1 day
M8	Admin Dashboard	Jinja2 or HTMX web UI for admin	1.5–2 days
M9	Cloud Deployment	EC2/GCP deploy, domain, HTTPS, optional CI/CD	1–2 days
M10	Monitoring + Polish	Add logging, error handling, testing, final polish	1 day


⸻

Timeline (Suggestion)

Week	Focus
Week 1	M0–M3: Core backend (auth, menu, orders)
Week 2	M4–M6: Reviews, preferences, AI features
Week 3	M7–M9: Uploads, admin UI, cloud deployment
Week 4	M10: Polish, write documentation, record demo

APIs
http://localhost:8000/auth/login/google