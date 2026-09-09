-- createRecipeFood.sql (Por el momento no se usara)
CREATE TABLE recipe_food (
    id BIGSERIAL PRIMARY KEY,
    recipe_id BIGINT REFERENCES recipe(id),
    food_id BIGINT REFERENCES food(id),
    quantity REAL,
    unit TEXT
);