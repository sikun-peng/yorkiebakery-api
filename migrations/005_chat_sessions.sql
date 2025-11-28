-- ============ CHAT SESSIONS ============
-- Stores conversation sessions for the AI chat feature
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

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_chat_session_id ON chat_session(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_user ON chat_session(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_session_expires ON chat_session(expires_at);

-- Clean up expired sessions automatically (optional)
-- You can run this periodically or set up a cron job
-- DELETE FROM chat_session WHERE expires_at < NOW();
