-- createUsersRecipes.sql (no se usa)
CREATE TABLE users_recipes (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    recipe_id BIGINT REFERENCES recipe(id)
);