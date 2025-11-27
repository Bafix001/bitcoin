from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os

app = FastAPI(title="Bitcoin Price Comparator API")

# CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'bitcoin_db'),
        user=os.getenv('POSTGRES_USER', 'bitcoin_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'bitcoin_password'),
        cursor_factory=RealDictCursor
    )

@app.get("/")
def read_root():
    return {"message": "Bitcoin Price Comparator API"}

@app.get("/prices/latest")
def get_latest_prices():
    """Récupère les derniers prix de chaque exchange"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT ON (exchange)
        exchange,
        price,
        quantity,
        symbol,
        datetime
    FROM bitcoin_prices
    WHERE datetime > NOW() - INTERVAL '1 minute'
    ORDER BY exchange, datetime DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"data": results}

@app.get("/prices/best")
def get_best_prices():
    """Trouve les meilleurs prix d'achat et de vente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        exchange,
        MIN(price) as best_buy_price,
        MAX(price) as best_sell_price,
        AVG(price) as avg_price,
        COUNT(*) as trade_count
    FROM bitcoin_prices
    WHERE datetime > NOW() - INTERVAL '1 minute'
    GROUP BY exchange
    ORDER BY best_buy_price ASC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"data": results}

@app.get("/prices/history")
def get_price_history(minutes: int = 5):
    """Récupère l'historique des prix"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        exchange,
        price,
        datetime
    FROM bitcoin_prices
    WHERE datetime > NOW() - INTERVAL '%s minutes'
    ORDER BY datetime DESC
    LIMIT 100
    """
    
    cursor.execute(query, (minutes,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"data": results}

@app.get("/prices/arbitrage")
def get_arbitrage_opportunities():
    """Trouve les opportunités d'arbitrage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    WITH recent_prices AS (
        SELECT DISTINCT ON (exchange)
            exchange,
            price,
            datetime
        FROM bitcoin_prices
        WHERE datetime > NOW() - INTERVAL '30 seconds'
        ORDER BY exchange, datetime DESC
    )
    SELECT 
        (SELECT exchange FROM recent_prices ORDER BY price ASC LIMIT 1) as buy_exchange,
        (SELECT price FROM recent_prices ORDER BY price ASC LIMIT 1) as buy_price,
        (SELECT exchange FROM recent_prices ORDER BY price DESC LIMIT 1) as sell_exchange,
        (SELECT price FROM recent_prices ORDER BY price DESC LIMIT 1) as sell_price,
        ((SELECT price FROM recent_prices ORDER BY price DESC LIMIT 1) - 
         (SELECT price FROM recent_prices ORDER BY price ASC LIMIT 1)) as profit,
        (((SELECT price FROM recent_prices ORDER BY price DESC LIMIT 1) - 
          (SELECT price FROM recent_prices ORDER BY price ASC LIMIT 1)) / 
         (SELECT price FROM recent_prices ORDER BY price ASC LIMIT 1) * 100) as profit_percentage
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {"data": result}