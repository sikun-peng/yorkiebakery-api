-- ================================================
-- Purge unverified users older than 24 hours
-- ================================================

DELETE FROM user_account
WHERE is_verified = FALSE
  AND created_at < NOW() - INTERVAL '24 hours';
