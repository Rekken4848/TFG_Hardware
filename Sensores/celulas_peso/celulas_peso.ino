#include "HX711.h"
#define SCK 23  //SALIDA SCK
#define DT 22   //ENTRADA DT
HX711 Bascula;

void setup() {
  Serial.println("Iniciando bascula");
  Serial.begin(9600);
  Bascula.begin(DT, SCK);
}

void loop() {
  delay(1000);
  if (Bascula.is_ready()) {
    long lectura = Bascula.read();
    Serial.println(lectura);
  } else {
    Serial.println("Bascula no lista");
  }
  Serial.println("\n\nCALIBRACION\n===========");
  Serial.println("Remueve todo el peso de la báscula y presiona enter");
  while (Serial.available()) Serial.read();
  while (Serial.available() == 0)
    ;
  Serial.println("Determinar offset");
  Bascula.tare(20);  // Promedio de 20 mediciones
  uint32_t offset = Bascula.get_offset();
   Bascula.set_offset(offset);
  Serial.print("OFFSET: ");
  Serial.println(offset);
  Serial.println();
  Serial.println("Pon una carga e ingresa su peso en gramos sin decimales ");
  //  flush Serial input
  while (Serial.available()) Serial.read();
  uint32_t weight = 0;
  while (weight == 0) {
    if (Serial.available()) {
      char ch = Serial.read();
      if (isdigit(ch)) {

        weight *= 10;
        weight = weight + (ch - '0');
      }
    }
  }
  Serial.print("Peso: ");
  Serial.println(weight);
  Bascula.calibrate_scale(weight, 20);
  float scale = Bascula.get_scale();

  Serial.print("SCALE:  ");
  Serial.println(scale, 6);

  Serial.print("\n Usa scale.set_offset(");
  Serial.print(offset);
  Serial.print("); Y scale.set_scale(");
  Serial.print(scale, 6);
  Serial.print(");\n");
  Serial.println("En el setup de tu código");
  Serial.println("\n\n");
}