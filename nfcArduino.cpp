#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN  9    
#define SS_PIN   10   
#define LED_PIN  8
#define BUZZER   7

MFRC522 mfrc522(SS_PIN, RST_PIN);

// Notas (frecuencias) y duraciones de la intro de Super Mario Bros (versión adaptada)
int melody[] = {
  660, 660, 0, 660, 0, 520, 660, 0, 730
};


int noteDurations[] = {
  100, 100, 100, 100, 100, 100, 100, 100, 100
};

void playMarioIntro() {
  for (int i = 0; i < sizeof(melody) / sizeof(int); i++) {
    int noteDuration = noteDurations[i];
    if (melody[i] == 0) {
      delay(noteDuration);
    } else {
      tone(BUZZER, melody[i], noteDuration);
      delay(noteDuration);
      noTone(BUZZER);
    }
    delay(30); // pequeña pausa entre notas
  }
}

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
      digitalWrite(LED_PIN, HIGH);
      
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);   
      } 
      Serial.println();
      mfrc522.PICC_HaltA();  
      //if (Serial.available()){
        //String response = Serial.readStringUntil('\n');
        //Serial.print("Respuesta de la Raspi: ");
        //Serial.println(response);
      //}
    }
      // Aquí suena la intro de Mario Bros
      playMarioIntro();

      delay(1000); 
  }      
  digitalWrite(LED_PIN, LOW);
}	
  
