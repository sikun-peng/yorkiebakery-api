# initilization
source venv/bin/activate
pip install -r requirements.txt

# shell into container
docker exec -it yorkiebakery-api-web /bin/bash

# docker cleanup
docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker image prune -f

# nuclear cleanup
docker-compose down --volumes
docker rmi $(docker images -q yorkiebakery-api_web)
docker builder prune -af

# docker build cmd
docker-compose build --no-cache && docker-compose up -d
docker-compose build && docker-compose up -d

# build frontend locally
cd ai_demo_frontend/
npm install
npm run build

# Run migrations
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/001_create_tables.sql
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/002_seed_menu.sql
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/003_seed_music.sql
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery -f /migrations/004_mock_menu.sql

# SSH into Postgres container
docker exec -it yorkiebakery-api-db psql -U postgres -d yorkiebakery

# Reset database (Danger!)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'yorkiebakery';

DROP DATABASE yorkiebakery;
CREATE DATABASE yorkiebakery WITH ENCODING 'UTF8' TEMPLATE template0;

# run embedding script
docker exec -it yorkiebakery-api-web python -m app.ai.run_embeddings

curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "thai food"}'

# prod docker-compose (pull from GHCR)
docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d

# clean up vector store
docker run --rm -v yorkiebakery-api_vector_store:/data alpine sh -c "mkdir -p /data && chmod 777 /data"

# purge css
curl -X POST "https://api.cloudflare.com/client/v4/zones/8547f59bcabb275c176448c50fa99867/purge_cache" \
  -H "Authorization: Bearer {}" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://beta.yorkiebakery.com/static/styles.css"]}'
