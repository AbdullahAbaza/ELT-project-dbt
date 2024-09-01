import subprocess
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], 
                ckeck=True, capture_output=True, text=True
            )
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries+=1
            print(
                f"Retrying in {delay_seconds} seconds... (Attemp {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
            print("Max retries reached. Exiting.")
            return False
# Using the function to check the connection to the source database 
# before running the ELT process

if not wait_for_postgres(host="source_postgres"):
    exit(1)
    

print("Starting ELT script... ")

# Configuration for the source PostgreSQL database
source_config = {
    'dbname' : 'sourcedb',
    'user' : 'postgres',
    'password' : 'postgres',
    'host' : 'source_postgres' # service name from docker-compose as the hostname
}


# Configuration for the destination PostgreSQL database
destination_config = {
    'dbname' : 'desination_db',
    'user' : 'postgres',
    'password' : 'postgres',
    'host' : 'desination_postgres'
}


# Using the pg_dump tool to dump the source database to SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    'U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w' # do not prompt for password
]

# Setting the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWRD=source_config['password'])

# excuting the dump command 
# check=True raises a CalledProcessError if the command returns a non-zero exit code.
subprocess.run(dump_command, env=subprocess_env, check=True)


# Using th psql tool to load the dumped SQL file into the destination database

load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql' # -a Print all nonempty input lines to standard output as they are read
]
# Setting the PGPASSWORD environment variable for the destination database
subprocess_env = dict(PGPASSWORD=destination_config['password'])

# Excute the load command 
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT Script")

