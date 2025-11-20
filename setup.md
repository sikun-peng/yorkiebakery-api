# initilization
source venv/bin/activate
pip install -r requirements.txt

# docker exec -it yorkiebakery-api-web /bin/bash

# docker build and run
docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker-compose down && docker-compose build && docker-compose up -d

# Run migrations
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/001_create_tables.sql
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/002_seed_menu.sql
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/003_seed_music.sql
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/004_mock_menu.sql

# SSH into Postgres container and reset database
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery

SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'yorkiebakery';

DROP DATABASE yorkiebakery;
CREATE DATABASE yorkiebakery WITH ENCODING 'UTF8' TEMPLATE template0;


# run embedding script to populate FAISS index
docker exec -it yorkiebakery-api-web python -m app.ai.run_embeddings

curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "thai food"}'

# build frontend
cd ai_demo_frontend/
npm run build