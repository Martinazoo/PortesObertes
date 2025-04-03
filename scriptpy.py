import serial
import time
import requests
arduino_port = '/dev/ttyACM0'
api_url = "http://127.0.0.1:8000/uuid_save"
baud_rate = 9600
timeout = 2

try: 
    ser = serial.Serial(arduino_port, baud_rate, timeout = timeout)
    time.sleep(2)
    print(f"Connectat a {arduino_port}")
except Exception as e:
    print(f"No es pot connectar al port {arduino_port}: {e}")
    exit()

def read_data():
    try:
        while True:
            uuid = ser.readline().decode('utf-8').strip()
            uuid_str = str(uuid)
            if uuid_str:
                print(uuid_str)
                object = {'uuid': uuid_str}
                response = requests.post(api_url, json = object)
                if response.status_code == 200:
                   print(f"UUID guardat: {uuid_str}")
                else:
                   print(f"Hi ha algun error: {response.text}")
    except KeyboardInterrupt:
        print("Finalitzat per l'usuari")
    finally:
        ser.close()
        print("Connexio acabada")
        

read_data()

#Fer crida a la bbdd i depen de si esta a la base de dades o no fer una cosa o una altra