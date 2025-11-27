-- Création de la table bitcoin_prices
CREATE TABLE IF NOT EXISTS bitcoin_prices (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    timestamp BIGINT NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    quantity DECIMAL(18, 8),
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_exchange_datetime ON bitcoin_prices(exchange, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_datetime ON bitcoin_prices(datetime DESC);
CREATE INDEX IF NOT EXISTS idx_exchange ON bitcoin_prices(exchange);

-- Afficher un message de confirmation
DO $$
BEGIN
    RAISE NOTICE '✅ Table bitcoin_prices créée avec succès';
END $$;