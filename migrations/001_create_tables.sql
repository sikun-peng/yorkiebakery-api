-- Enable UUID
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
    verification_token TEXT
);

-- ============ MENU ITEMS ============
DROP TABLE IF EXISTS menu_item CASCADE;
CREATE TABLE menu_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT,
    origin TEXT,
    category TEXT,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    flavor_profile TEXT[] DEFAULT ARRAY[]::TEXT[],
    dietary_restrictions TEXT[] DEFAULT ARRAY[]::TEXT[],
    price NUMERIC(10,2),
    is_available BOOLEAN DEFAULT TRUE
);

-- ============ CART ============
DROP TABLE IF EXISTS cart CASCADE;
CREATE TABLE cart (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_account(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS cart_item CASCADE;
CREATE TABLE cart_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES cart(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_item(id) ON DELETE CASCADE,
    quantity INT DEFAULT 1
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