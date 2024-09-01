import subprocess
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], 
                check=True, capture_output=True, text=True
            )
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
       
    print("Max retries reached. Exiting.")
    return False

# Check connection to the source database before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    exit(1)

# Check connection to the destination database before running the ELT process
if not wait_for_postgres(host="destination_postgres"):
    exit(1)


print("Starting ELT script...")

# Configuration for the source PostgreSQL database
source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'source_postgres'  # service name from docker-compose as the hostname
}

# Configuration for the destination PostgreSQL database
destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'destination_postgres'
}

# Using the pg_dump tool to dump the source database to SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'  # do not prompt for password
]

# Setting the PGPASSWORD environment variable to avoid password prompt
source_env = dict(PGPASSWORD=source_config['password'])

try:
    subprocess.run(dump_command, env=source_env, check=True)
except subprocess.CalledProcessError as e:
    print(f"pg_dump failed: {e}")
    exit(1)

# Using the psql tool to load the dumped SQL file into the destination database
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

# Setting the PGPASSWORD environment variable for the destination database
destination_env = dict(PGPASSWORD=destination_config['password'])

try:
    subprocess.run(load_command, env=destination_env, check=True)
except subprocess.CalledProcessError as e:
    print(f"psql load failed: {e}")
    exit(1)

print("Ending ELT script")
