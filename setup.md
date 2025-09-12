source venv/bin/activate

docker stop $(docker ps -q)
docker rm $(docker ps -a -q)

docker-compose down && docker-compose build && docker-compose up -d


docker exec -it yorkiebakery-api-db-1 psql -U postgres -d yorkiebakery



UPDATE "user" SET is_admin = true WHERE email = 'admin@yorkie.com';