import websocket
from kafka import KafkaProducer
import json
from datetime import datetime
import threading
import os

# Initialiser le producer Kafka
producer = KafkaProducer(
    bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ==================== BINANCE ====================
def on_message_binance(ws, message):
    try:
        data = json.loads(message)
        bitcoin_data = {
            'exchange': 'binance',
            'timestamp': int(data['E']),
            'price': float(data['p']),
            'quantity': float(data['q']),
            'symbol': 'BTCUSDT',
            'datetime': datetime.now().isoformat()
        }
        producer.send('bitcoin-prices', bitcoin_data)
        print(f"✓ [BINANCE] ${bitcoin_data['price']}")
    except Exception as e:
        print(f"✗ [BINANCE] Erreur: {e}")

def binance_stream():
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_message=on_message_binance,
        on_open=lambda ws: print("🟢 [BINANCE] Connecté"),
        on_error=lambda ws, error: print(f"🔴 [BINANCE] Erreur: {error}")
    )
    ws.run_forever()

# ==================== COINBASE ====================
def on_message_coinbase(ws, message):
    try:
        data = json.loads(message)
        if data.get('type') == 'ticker' and data.get('product_id') == 'BTC-USD':
            bitcoin_data = {
                'exchange': 'coinbase',
                'timestamp': int(datetime.now().timestamp() * 1000),
                'price': float(data['price']),
                'quantity': float(data.get('last_size', 0)),
                'symbol': 'BTCUSD',
                'datetime': datetime.now().isoformat()
            }
            producer.send('bitcoin-prices', bitcoin_data)
            print(f"✓ [COINBASE] ${bitcoin_data['price']}")
    except Exception as e:
        print(f"✗ [COINBASE] Erreur: {e}")

def on_open_coinbase(ws):
    print("🟢 [COINBASE] Connecté")
    subscribe_message = {
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channels": ["ticker"]
    }
    ws.send(json.dumps(subscribe_message))

def coinbase_stream():
    ws = websocket.WebSocketApp(
        "wss://ws-feed.exchange.coinbase.com",
        on_message=on_message_coinbase,
        on_open=on_open_coinbase,
        on_error=lambda ws, error: print(f"🔴 [COINBASE] Erreur: {error}")
    )
    ws.run_forever()

# ==================== KRAKEN ====================
def on_message_kraken(ws, message):
    try:
        data = json.loads(message)
        if data.get('channel') == 'trade' and isinstance(data.get('data'), list):
            for trade in data['data']:
                bitcoin_data = {
                    'exchange': 'kraken',
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'price': float(trade['price']),
                    'quantity': float(trade['qty']),
                    'symbol': 'BTCUSD',
                    'datetime': datetime.now().isoformat()
                }
                producer.send('bitcoin-prices', bitcoin_data)
                print(f"✓ [KRAKEN] ${bitcoin_data['price']}")
    except Exception as e:
        print(f"✗ [KRAKEN] Erreur: {e}")

def on_open_kraken(ws):
    print("🟢 [KRAKEN] Connecté")
    subscribe_message = {
        "method": "subscribe",
        "params": {
            "channel": "trade",
            "symbol": ["BTC/USD"]
        }
    }
    ws.send(json.dumps(subscribe_message))

def kraken_stream():
    ws = websocket.WebSocketApp(
        "wss://ws.kraken.com/v2",
        on_message=on_message_kraken,
        on_open=on_open_kraken,
        on_error=lambda ws, error: print(f"🔴 [KRAKEN] Erreur: {error}")
    )
    ws.run_forever()

# ==================== MAIN ====================
if __name__ == "__main__":
    print("🚀 Démarrage du Producer Multi-Exchanges...")
    
    # Lancer les 3 WebSockets en parallèle avec threading
    binance_thread = threading.Thread(target=binance_stream, daemon=True)
    coinbase_thread = threading.Thread(target=coinbase_stream, daemon=True)
    kraken_thread = threading.Thread(target=kraken_stream, daemon=True)
    
    binance_thread.start()
    coinbase_thread.start()
    kraken_thread.start()
    
    # Garder le programme en vie
    binance_thread.join()
    coinbase_thread.join()
    kraken_thread.join()