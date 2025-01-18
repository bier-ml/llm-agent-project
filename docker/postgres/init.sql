-- Create tables with timestamps defaults and foreign key constraints

-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- News Table
CREATE TABLE news (
    news_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    source VARCHAR(255),
    published_at TIMESTAMP,
    sentiment_score FLOAT,
    tags JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crypto_Tokens Table
CREATE TABLE crypto_tokens (
    token_id SERIAL PRIMARY KEY,
    token_name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    market_cap BIGINT,
    price FLOAT,
    volume_24h BIGINT,
    circulating_supply BIGINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historical_Data Table
CREATE TABLE historical_data (
    data_id SERIAL PRIMARY KEY,
    token_id INT REFERENCES crypto_tokens(token_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    price_open FLOAT,
    price_close FLOAT,
    price_high FLOAT,
    price_low FLOAT,
    volume BIGINT
);

-- Recommendations Table
CREATE TABLE recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    token_id INT REFERENCES crypto_tokens(token_id) ON DELETE CASCADE,
    news_id INT REFERENCES news(news_id) ON DELETE CASCADE,
    recommendation TEXT,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs Table
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    event_type VARCHAR(50),
    event_details JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_historical_data_token_id ON historical_data(token_id);
CREATE INDEX idx_historical_data_date ON historical_data(date);
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_token_id ON recommendations(token_id);
CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_event_type ON logs(event_type); 