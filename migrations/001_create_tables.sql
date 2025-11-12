-- Enable UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============ USERS ============
CREATE TABLE IF NOT EXISTS user_account (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ MENU ITEMS ============
DROP TABLE IF EXISTS menu_item CASCADE;
CREATE TABLE menu_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT,
    cuisine TEXT,
    dish_type TEXT,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    flavor_profile TEXT[] DEFAULT ARRAY[]::TEXT[],
    dietary_restrictions TEXT[] DEFAULT ARRAY[]::TEXT[],
    price NUMERIC(10,2),
    is_available BOOLEAN DEFAULT TRUE
);

-- ============ REVIEWS ============
CREATE TABLE IF NOT EXISTS review (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_account(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_item(id) ON DELETE CASCADE,
    rating INT CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ ORDERS ============
CREATE TABLE IF NOT EXISTS order_record (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_account(id) ON DELETE CASCADE,
    order_details JSONB NOT NULL,
    total_price NUMERIC(10,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ CAMPAIGNS ============
CREATE TABLE IF NOT EXISTS campaign (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE
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