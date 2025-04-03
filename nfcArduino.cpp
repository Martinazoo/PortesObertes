#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN	9    
#define SS_PIN	10   
#define LED_PIN 8

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
	Serial.begin(9600); 
	SPI.begin();        
  pinMode(LED_PIN, OUTPUT);
	mfrc522.PCD_Init(); 
}

void loop() {
	if ( mfrc522.PICC_IsNewCardPresent()){  
    if ( mfrc522.PICC_ReadCardSerial()) {
      digitalWrite(LED_PIN, HIGH);
          for (byte i = 0; i < mfrc522.uid.size; i++) {
            Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
            Serial.print(mfrc522.uid.uidByte[i], HEX);   
          } 
          Serial.println();
          mfrc522.PICC_HaltA();  
          delay(1000);       
    }      
	}	
  
  digitalWrite(LED_PIN, LOW);
}