docker compose up airflow-postgres -d
sleep 5
docker compose up airflow-init
sleep 10
docker compose up -d
sleep 5

cd airbyte/

if [ -f "docker-compose.yaml" ]; then
    docker compose up -d
else
    ./run-ab-platform.sh
fi


