-- createFood.sql
CREATE TABLE food (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    quantity TEXT,
    product_quantity REAL,
    product_quantity_unit TEXT,
    serving_size TEXT,
    calories_per_serving REAL,
    calories_per_100g REAL,
    proteins_per_100g REAL,
    fat_per_100g REAL,
    carbs_per_100g REAL,
    sugars_per_100g REAL,
    fiber_per_100g REAL,
    image TEXT,
    nutriscore TEXT,
    allergens TEXT[],
    ingredients TEXT,
    countries TEXT[]
);