from kafka import KafkaConsumer
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Connexion à PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="bitcoin_db",
    user="bitcoin_user",
    password="bitcoin_password"
)
cursor = conn.cursor()

print("✅ Connecté à PostgreSQL")

# Consumer Kafka
consumer = KafkaConsumer(
    'bitcoin-prices',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='bitcoin-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("✅ Connecté à Kafka")
print("🔄 En attente de messages...\n")

# Lire les messages et les insérer en BD
for message in consumer:
    try:
        data = message.value
        
        # Insérer dans PostgreSQL
        insert_query = """
        INSERT INTO bitcoin_prices (exchange, timestamp, price, quantity, symbol, datetime)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            data['exchange'],
            data['timestamp'],
            data['price'],
            data['quantity'],
            data['symbol'],
            data['datetime']
        ))
        
        conn.commit()
        
        print(f"💾 [{data['exchange'].upper()}] ${data['price']} → BD")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()