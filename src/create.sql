CREATE TABLE stocks (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, ticker)
);

CREATE TABLE coins (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    coin_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, coin_id)
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    price_updates BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stocks_user_id ON stocks(user_id);
CREATE INDEX idx_coins_user_id ON coins(user_id);

ALTER TABLE stocks
ADD CONSTRAINT fk_stocks_user
FOREIGN KEY (user_id)
REFERENCES users(user_id)
ON DELETE CASCADE;

ALTER TABLE coins
ADD CONSTRAINT fk_coins_user
FOREIGN KEY (user_id)
REFERENCES users(user_id)
ON DELETE CASCADE;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.stocks public.coins public.users TO anon, authenticated, service_role;