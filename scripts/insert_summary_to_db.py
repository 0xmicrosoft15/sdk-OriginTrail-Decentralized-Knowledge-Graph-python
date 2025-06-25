import os
import sys
import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

MAINNET_PORTS = [':8453', ':100', ':2043']
files = sys.argv[1:]

def is_mainnet(blockchain_name):
    return any(blockchain_name.endswith(port) for port in MAINNET_PORTS)

def get_db_connection(mainnet=False):
    host = os.getenv('DB_HOST_MAINNET') if mainnet else os.getenv('DB_HOST_TESTNET')
    return psycopg2.connect(
        host=host,
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        dbname=os.getenv('DB_NAME'),
        port=os.getenv('DB_PORT', 5432)
    )

for file in files:
    print(f"Processing {file}")
    try:
        with open(file, 'r') as f:
            summary = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read or parse {file}: {e}")
        continue

    blockchain_name = summary.get('blockchain_name', '')
    mainnet = is_mainnet(blockchain_name)
    table_name = 'publish_mainnet_summary' if mainnet else 'publish_testnet_summary'

    try:
        conn = get_db_connection(mainnet)
        cursor = conn.cursor()
        print(f"✅ Connected to DB ({'mainnet' if mainnet else 'testnet'})")

        insert_query = sql.SQL(f"""
            INSERT INTO {table_name} (
                blockchain_name, node_name,
                publish_success_rate, query_success_rate,
                publisher_get_success_rate, non_publisher_get_success_rate,
                average_publish_time, average_query_time,
                average_publisher_get_time, average_non_publisher_get_time,
                time_stamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

        cursor.execute(insert_query, (
            summary.get('blockchain_name'),
            summary.get('node_name'),
            summary.get('publish_success_rate'),
            summary.get('query_success_rate'),
            summary.get('publisher_get_success_rate'),
            summary.get('non_publisher_get_success_rate'),
            summary.get('average_publish_time'),
            summary.get('average_query_time'),
            summary.get('average_publisher_get_time'),
            summary.get('average_non_publisher_get_time'),
            summary.get('time_stamp'),
        ))

        conn.commit()
        print(f"✅ Inserted {file} into table '{table_name}'")

    except Exception as e:
        print(f"❌ Failed to insert {file} into DB (table '{table_name}'): {e}")

    finally:
        try:
            cursor.close()
            conn.close()
            print("✅ DB connection closed")
        except Exception as e:
            print(f"❌ Failed to close DB connection: {e}")