-- createUserStats.sql (no se usa)
CREATE TABLE user_daily_goals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(id),
    calories REAL,
    protein REAL,
    carbohydrates REAL,
    fat REAL,
    goals_date DATE NOT NULL
);