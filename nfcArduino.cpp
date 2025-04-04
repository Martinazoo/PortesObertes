#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN  9    
#define SS_PIN   10   
#define LED_PIN  8
#define BUZZER   7

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600); 
  SPI.begin();        
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  mfrc522.PCD_Init(); 
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent()) {  
    if (mfrc522.PICC_ReadCardSerial()) {
      //Serial print para connectarme con la raspi 
      digitalWrite(LED_PIN, HIGH);
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);   
      } 
      Serial.println();
      mfrc522.PICC_HaltA();  

      int melody[] = {659, 622, 659, 622, 659, 494, 587, 523, 440, 440, 494, 523}; 
      int durations[] = {150, 150, 150, 150, 150, 150, 150, 150, 250, 150, 150, 300}; 

      for (int i = 0; i < 12; i++) {
        tone(BUZZER, melody[i], durations[i]);
        delay(durations[i] * 1.3);
        noTone(BUZZER);
      }

      delay(1000); 
    }      
  }	
  
  digitalWrite(LED_PIN, LOW);
}
//Funcion lectura de NFCID i otra para obtener la respuesta 