import socket
import requests
import json


def enviar_datos(datos):
    # Formatear los datos
    #Divide la cadena datos en líneas utilizando split('\n'), Itera sobre cada línea.
    latitud, longitud, altitud, timestamp, rpm = [line.split(': ')[1] for line in datos.split('\n') if line]
    datos_formateados = {
        'latitud': float(latitud),
        'longitud': float(longitud),
        'altitud': float(altitud),
        'timestamp': timestamp,
        #'speed': float(speed),  
        'rpm': float(rpm), 
    }

    # Convertir a JSON y enviar
    url = 'http://127.0.0.1:5000/recibir_data'
    headers = {'Content-Type': 'application/json'}
    response_post = requests.post(url, json=datos_formateados, headers=headers)
    print("Respuesta POST:", response_post.text)

def main():
    host = ''
    puerto = 8888

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor:
        servidor.bind((host, puerto))
        print(f"Servidor UDP escuchando en el puerto {puerto}...")

        while True:
            datos_recibidos, direccion_cliente = servidor.recvfrom(1024)
            datos_decodificados = datos_recibidos.decode('utf-8')
            print("Datos recibidos:", datos_decodificados)

            # Enviar los datos al servidor Flask
            enviar_datos(datos_decodificados)

if __name__ == "__main__":
    main()
