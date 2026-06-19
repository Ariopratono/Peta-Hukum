import psycopg2
import os

# Default Odoo config values
DBNAME = os.environ.get('PGDATABASE', 'odoo')
USER = os.environ.get('PGUSER', 'odoo')
PASSWORD = os.environ.get('PGPASSWORD', 'odoo')
HOST = os.environ.get('PGHOST', 'localhost')
PORT = os.environ.get('PGPORT', '5432')

try:
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()[0]
    print('PostgreSQL version:', version)
    cur.close()
    conn.close()
except Exception as e:
    print('Failed to connect to PostgreSQL:', e)
