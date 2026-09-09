-- createTemperatureHumidity.sql
CREATE TABLE temperature_humidity (
    id BIGSERIAL PRIMARY KEY,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL
);