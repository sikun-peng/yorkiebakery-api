# initilization
source venv/bin/activate
pip install -r requirements.txt

# docker build and run
docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker-compose down && docker-compose build && docker-compose up -d

# Run migrations
docker exec -it yorkiebakery-api-db-1 psql -U postgres -d yorkiebakery -f /migrations/001_create_tables.sql
docker exec -it yorkiebakery-api-db-1 psql -U postgres -d yorkiebakery -f /migrations/002_seed_menu.sql
docker exec -it yorkiebakery-api-db-1 psql -U postgres -d yorkiebakery -f /migrations/003_seed_music.sql

# docker exec -it yorkiebakery-api_db_1 psql -U postgres
docker exec -it yorkiebakery-api-db-1 psql -U postgres -d yorkiebakery

SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'yorkiebakery';

DROP DATABASE yorkiebakery;

CREATE DATABASE yorkiebakery;


# run embedding script to populate FAISS index
docker exec -it yorkiebakery-api-web-1 python -m app.ai.run_embeddings

curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "thai", "top_k": 5, "filters": {"origin": "thai"}}'

UPDATE "user" SET is_admin = true WHERE email = 'admin@yorkie.com';


docker exec -it yorkiebakery-api-web-1 /bin/bash