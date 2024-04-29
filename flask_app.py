from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Variable de entorno
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

# Configuración de la base de datos MySQL
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME")
)

db_config = {
    'host': os.environ.get("DB_HOST"),
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get("DB_PASSWORD"),
    'database': os.environ.get("DB_NAME")
}


@app.route('/tiempo_real', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return render_template('pag1.html')
    else:
        return render_template('pag1.html')

@app.route('/recibir_coordenadas', methods=['POST'])
def recibir_udp():
    data = request.json
    print("Datos recibidos en la solicitud POST:", data)

    # Extraer los valores de latitud, longitud, altitud y timestamp
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    altitud = data.get('altitud')
    timestamp = data.get('timestamp')

    # Insertar los datos en la base de datos MySQL
    cursor = db.cursor()
    insert_query = "INSERT INTO coordenadas (latitud, longitud, altitud, timestamp) VALUES (%s, %s, %s, %s)"
    data_tuple = (latitud, longitud, altitud, timestamp)
    cursor.execute(insert_query, data_tuple)
    db.commit()
    cursor.close()

    # Emitir los datos al cliente WebSocket
    socketio.emit('update_coords', {'latitud': latitud, 'longitud': longitud, 'altitud': altitud, 'timestamp': timestamp})
    print("Datos enviados al cliente WebSocket:", {'latitud': latitud, 'longitud': longitud, 'altitud': altitud, 'timestamp': timestamp})
    return 'Datos recibidos y procesados correctamente'

@app.route('/recibir_data', methods=['POST'])
def recibir_elm():
    data = request.json
    print("Datos recibidos en la solicitud POST:", data)

    # Extraer los valores de latitud, longitud, altitud y timestamp
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    altitud = data.get('altitud')
    timestamp = data.get('timestamp')
    #speed = data.get('speed')
    rpm = data.get('rpm')

    # Insertar los datos en la base de datos MySQL
    cursor = db.cursor()
    insert_query = "INSERT INTO datos (latitud, longitud, altitud, timestamp, rpm) VALUES (%s, %s, %s, %s, %s)"
    data_tuple = (latitud, longitud, altitud, timestamp, rpm)
    cursor.execute(insert_query, data_tuple)
    db.commit()
    cursor.close()

    print("Datos:", {'latitud': latitud, 'longitud': longitud, 'altitud': altitud, 'timestamp': timestamp, 'rpm': rpm})

    # Emitir los datos al cliente WebSocket
    #socketio.emit('update_data', {'latitud': latitud, 'longitud': longitud, 'altitud': altitud, 'timestamp': timestamp, 'speed': speed, 'rpm': rpm})
    #print("Datos enviados al cliente WebSocket:", {'latitud': latitud, 'longitud': longitud, 'altitud': altitud, 'timestamp': timestamp,  'speed': speed, 'rpm': rpm})
    #return 'Datos recibidos y procesados correctamente'



@app.route('/consulta_historica', methods=['POST'])
def consultar_historial():
    inicio = request.form.get('inicio')
    fin = request.form.get('fin')
    
    # Verifica si hay valores para inicio y fin
    if inicio is not None and fin is not None:
        # Realiza la conexión con la base de datos y ejecuta la consulta SQL
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor()
        consulta = ("SELECT Latitud, Longitud, Timestamp FROM coordenadas "
                    "WHERE timestamp >= %s AND timestamp <= %s")
        cursor.execute(consulta, (inicio, fin))
        coordenadas = cursor.fetchall()
        conexion.close()
        
        # Prepara las coordenadas para enviarlas al frontend
        coordenadas_json = [{'latitud': str(lat), 'longitud': str(lon), 'timestamp': str(ts)} for lat, lon, ts in coordenadas]
        
        # Devolver las coordenadas en formato JSON
        return jsonify({'coordenadas': coordenadas_json})
    
    # Si no hay valores para inicio y fin, solo muestra la página
    return render_template('pag2.html')

@app.route('/velocidad', methods=['POST'])
def consultar_velocidad():
    return render_template('pag3.html')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)



