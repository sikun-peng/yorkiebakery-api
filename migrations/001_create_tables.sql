-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============ USERS ============
DROP TABLE IF EXISTS user_account CASCADE;
CREATE TABLE user_account (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    last_login TIMESTAMP
);

-- ============ PASSWORD RESET TOKENS ============
CREATE TABLE IF NOT EXISTS password_reset_token (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_account(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_token_token ON password_reset_token(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_token_user_id ON password_reset_token(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_token_expires ON password_reset_token(expires_at);


-- ============ MENU ITEMS ============
DROP TABLE IF EXISTS menu_item CASCADE;
CREATE TABLE menu_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    gallery_urls TEXT[] DEFAULT ARRAY[]::TEXT[],
    origin TEXT,
    category TEXT,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    flavor_profiles TEXT[] DEFAULT ARRAY[]::TEXT[],
    dietary_features TEXT[] DEFAULT ARRAY[]::TEXT[],
    price NUMERIC(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    recipe TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ ORDERS ============
DROP TABLE IF EXISTS "order" CASCADE;
CREATE TABLE "order" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_account(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    total NUMERIC(10,2) DEFAULT 0
);

-- ============ ORDER ITEMS ============
DROP TABLE IF EXISTS order_item CASCADE;
CREATE TABLE order_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES "order"(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_item(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    quantity INT NOT NULL
);

-- ============ MUSIC ============
DROP TABLE IF EXISTS music_track CASCADE;
CREATE TABLE music_track (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    composer TEXT,
    performer TEXT,
    category TEXT,
    description TEXT,
    file_url TEXT NOT NULL,
    cover_url TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);


-- ============ EVENTS TABLE ============
DROP TABLE IF EXISTS event CASCADE;
CREATE TABLE IF NOT EXISTS event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    event_datetime TIMESTAMP,
    location TEXT,
    event_type TEXT,
    image_url TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);


-- ============ EVENT RSVPs ============
DROP TABLE IF EXISTS event_rsvp CASCADE;
CREATE TABLE IF NOT EXISTS event_rsvp (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES event(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_event_active ON event(is_active);
CREATE INDEX IF NOT EXISTS idx_rsvp_event_id ON event_rsvp(event_id);


-- ============ Menu Review ============
DROP TABLE IF EXISTS review CASCADE;
CREATE TABLE IF NOT EXISTS review (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    menu_item_id UUID NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_review_user_menu UNIQUE (user_id, menu_item_id),
    CONSTRAINT fk_review_user FOREIGN KEY(user_id)
        REFERENCES user_account(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_menu FOREIGN KEY(menu_item_id)
        REFERENCES menu_item(id) ON DELETE CASCADE
);


-- ============ CHAT SESSIONS ============
DROP TABLE IF EXISTS chat_session CASCADE;
CREATE TABLE chat_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES user_account(id) ON DELETE CASCADE,
    conversation_history JSONB DEFAULT '[]'::jsonb,
    preferences JSONB DEFAULT '{}'::jsonb,
    last_message_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX IF NOT EXISTS idx_chat_session_id ON chat_session(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_user ON chat_session(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_expires ON chat_session(expires_at);

-- Clean up expired sessions automatically (optional)
-- You can run this periodically or set up a cron job
-- DELETE FROM chat_session WHERE expires_at < NOW();
