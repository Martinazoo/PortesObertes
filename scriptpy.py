import serial
import time
import requests

arduino_port = '/dev/ttyACM0'
api_url = "http://127.0.0.1:8000/uuid_save"
baud_rate = 9600
timeout = 2

try: 
    ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
    time.sleep(2)
    print(f"Conectado a {arduino_port}")
except Exception as e:
    print(f"No se puede conectar al puerto {arduino_port}: {e}")
    exit()

def read_data():
    try:
        while True:
            uuid = ser.readline().decode('utf-8').strip()
            uuid_str = str(uuid)
            if uuid_str:
                print(uuid_str)
                data = {'uuid': uuid_str}  # Cambié 'object' por 'data'
                response = requests.post(api_url, json=data)
                if response.status_code == 200:
                    print(f"UUID guardado: {uuid_str}")
                   # print(response)
                    #ser.write((response).encode())
                else:
                    print(f"Hubo algún error: {response.text}")
                    print(response.status_code)
                    #ser.write((response).encode())
                    #print(response)
                    
    except KeyboardInterrupt:
        print("Finalizado por el usuario")
    finally:
        ser.close()
        print("Conexión terminada")
        

read_data()
