#include <ArduinoMqttClient.h>
#include <WiFi.h>
#include <DHT.h>
#include "HX711.h"

// --- WiFi Config ---
char ssid[] = "Moto G Play 4311";
char pass[] = "48484848";

// --- MQTT Config ---
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char broker[] = "192.168.43.205";
int port = 1883;
const char topicTempHum[] = "hmaresc/tfg/arduino/temhum";
const char topicPeso[] = "hmaresc/tfg/arduino/peso";

// --- DHT11 Config ---
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- HX711 Config ---
#define SCK 23
#define DT 22
HX711 bascula;

// ============================
// Conexión WiFi
// ============================
void setupWiFi() {
  Serial.print("Conectando a WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nWiFi conectado!");
}

// ============================
// Conexión MQTT
// ============================
void setupMQTT() {
  mqttClient.setId("esp32_dht_peso_rtos");
  while (!mqttClient.connect(broker, port)) {
    Serial.print("Fallo al conectar con MQTT, error: ");
    Serial.println(mqttClient.connectError());
    delay(1000);
  }
  Serial.println("Conectado al broker MQTT");
}

// ============================
// Tarea de temperatura y humedad
// ============================
void tareaTemHum(void *parameter) {
  for (;;) {
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (!isnan(h) && !isnan(t)) {
      String payload = String("{\"temperature\":") + t + ",\"humidity\":" + h + "}";
      Serial.println("[DHT11] Publicando:");
      Serial.println(payload);
      mqttClient.beginMessage(topicTempHum);
      mqttClient.print(payload);
      mqttClient.endMessage();
    } else {
      Serial.println("[DHT11] Error de lectura");
    }

    vTaskDelay(2000 / portTICK_PERIOD_MS);  // 2 segundos
  }
}

// ============================
// Tarea de lectura de báscula
// ============================
void tareaBascula(void *parameter) {
  for (;;) {
    if (bascula.is_ready()) {
      float pesoGramos = bascula.get_units(10) * 100;
      pesoGramos = round(pesoGramos * 100.0) / 100.0;

      if (pesoGramos >= 10) {
        String payload = String("{\"weight\":") + pesoGramos + "}";
        Serial.println("[Báscula] Publicando:");
        Serial.println(payload);
        mqttClient.beginMessage(topicPeso);
        mqttClient.print(payload);
        mqttClient.endMessage();
      } else {
        Serial.println("[Báscula] Peso bajo, no enviado");
      }
    } else {
      Serial.println("[Báscula] No lista");
    }

    vTaskDelay(2000 / portTICK_PERIOD_MS);  // 2 segundos
  }
}

// ============================
// SETUP
// ============================
void setup() {
  Serial.begin(9600);
  dht.begin();

  bascula.begin(DT, SCK);
  bascula.set_offset(98022);
  bascula.set_scale(-83201.523438);
  delay(2000);

  setupWiFi();
  setupMQTT();

  // Crear tareas FreeRTOS
  xTaskCreate(tareaTemHum, "Tarea DHT11", 4096, NULL, 1, NULL);
  xTaskCreate(tareaBascula, "Tarea Bascula", 4096, NULL, 1, NULL);
}

void loop() {
  mqttClient.poll();
}