#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22

#define LDR_PIN A0

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  int light = analogRead(LDR_PIN);

  if (isnan(temperature) || isnan(humidity)) {
    delay(2000);
    return;
  }

  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.println(light);

  delay(5000);
}
