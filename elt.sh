docker compose up airflow-postgres -d
sleep 5
docker compose up airflow-init
sleep 10
docker compose up -d
