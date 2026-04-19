#include <LiquidCrystal.h>

// LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 10, 9, 8, 4);

// Capteurs
int soilPin = A0;
int tempPin = A1;

// LEDs
int ledR = 7;
int ledY = 6;
int ledG = 5;

void setup() {
  lcd.begin(16, 2);
  Serial.begin(9600);

  pinMode(ledR, OUTPUT);
  pinMode(ledY, OUTPUT);
  pinMode(ledG, OUTPUT);

  lcd.print("System Start...");
  delay(2000);
  lcd.clear();
}

void loop() {
   
  // Lecture des valeurs
  */int soilValue = analogRead(soilPin);
  int tempValue = analogRead(tempPin);

  // Conversion
  int soilPercent = map(soilValue, 0, 1023, 0, 100);
  int tempC = map(tempValue, 0, 1023, 0, 50);

  // ===== LEDs =====
  if (soilPercent < 30) {
    digitalWrite(ledR, HIGH);
    digitalWrite(ledY, LOW);
    digitalWrite(ledG, LOW);
  }
  else if (soilPercent < 70) {
    digitalWrite(ledR, LOW);
    digitalWrite(ledY, HIGH);
    digitalWrite(ledG, LOW);
  }
  else {
    digitalWrite(ledR, LOW);
    digitalWrite(ledY, LOW);
    digitalWrite(ledG, HIGH);
  }

  // ===== LCD =====
  lcd.setCursor(0, 0);
  lcd.print("Temp:");
  lcd.print(tempC);
  lcd.print("C   ");  // nettoyage

  lcd.setCursor(0, 1);
  lcd.print("Soil:");
  lcd.print(soilPercent);
  lcd.print("%   "); // nettoyage

  // ===== Serial (CSV) =====
  Serial.print(tempC);
  Serial.print(",");
  Serial.println(soilPercent);

  delay(1000);
}