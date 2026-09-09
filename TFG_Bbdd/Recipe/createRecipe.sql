-- createRecipe.sql
CREATE TABLE recipe (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    recipe_name TEXT NOT NULL,
    recipe_description TEXT,
    recipe_category TEXT NOT NULL,
    recipe_diet TEXT,
    prep_time INTEGER NOT NULL, -- minutes
    cook_time INTEGER, -- minutes
    servings INTEGER NOT NULL,
    difficulty TEXT,
    emoji TEXT,
    image_file bytea,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    fiber REAL,
    sugar REAL,
    tags TEXT[]
);

-- Relación uno-a-muchos con ingredientes
CREATE TABLE recipe_ingredient (
    id BIGSERIAL PRIMARY KEY,
    recipe_id BIGINT NOT NULL REFERENCES recipe(id),
    quantity TEXT NOT NULL,
    unit TEXT NOT NULL,
    name TEXT NOT NULL
);

-- Relación uno-a-muchos con instrucciones
CREATE TABLE recipe_instruction (
    id BIGSERIAL PRIMARY KEY,
    recipe_id BIGINT NOT NULL REFERENCES recipe(id),
    step_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    time TEXT NOT NULL
);