import psycopg2
from config import load_config


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def create_table():
    """ Create the phonebook table if not exists """
    command = """
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(command)
            conn.commit()
            print('Table "phonebook" ready.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def create_functions_and_procedures():
    """ Execute SQL files to create functions and procedures """
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Create functions
                with open('functions.sql', 'r') as f:
                    cur.execute(f.read())
                # Create procedures
                with open('procedures.sql', 'r') as f:
                    cur.execute(f.read())
            conn.commit()
            print('Functions and procedures created successfully.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == '__main__':
    config = load_config()
    connect(config)
    create_table()
    create_functions_and_procedures()
