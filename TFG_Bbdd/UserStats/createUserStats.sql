-- createUserStats.sql
CREATE TABLE user_stats (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id),
    profile_image bytea,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    height REAL NOT NULL,
    weight REAL NOT NULL,
    activity_level TEXT NOT NULL,
    fat_percentage REAL NOT NULL
);