docker compose up aitflow-postgres
sleep 5
docker compose up aitflow-init
sleep 10
docker compose up -d
sleep 5

cd /airbyte

if [ -f "docker-compose.yaml" ]; then
    docker compose up -d
else
    ./run-ab-platform.sh
fi


