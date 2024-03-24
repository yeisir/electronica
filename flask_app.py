from flask import Flask, render_template, request
from flask_socketio import SocketIO
import mysql.connector
import os
from dotenv import load_dotenv

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

@app.route('/tiempo_real')
def index():
    return render_template('pag1.html')

@app.route('/recibir_udp', methods=['GET', 'POST'])
def recibir_udp():
    if request.method == 'GET':
        # Si la solicitud es GET, obtener los datos de la consulta
        latitud = request.args.get('latitud')
        longitud = request.args.get('longitud')
        altitud = request.args.get('altitud')
        timestamp = request.args.get('timestamp')
    elif request.method == 'POST':
        # Si la solicitud es POST, obtener los datos del cuerpo JSON
        data = request.json
        print("Datos recibidos en la solicitud POST:", data)

        # Extraer los valores de latitud, longitud, altitud y timestamp
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        altitud = data.get('altitud')
        timestamp = data.get('timestamp')
    else:
        # Si la solicitud no es ni GET ni POST, retornar un mensaje de error
        return 'Método no permitido'

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

# Función para obtener coordenadas históricas desde la base de datos
def obtener_coordenadas_historicas(inicio, fin):
    cursor = db.cursor()
    select_query = "SELECT latitud, longitud FROM coordenadas WHERE timestamp BETWEEN %s AND %s"
    cursor.execute(select_query, (inicio, fin))
    coordenadas_historicas = cursor.fetchall()
    cursor.close()
    return coordenadas_historicas

@app.route('/consulta_historica', methods=['GET', 'POST'])
def consulta_historica():
    if request.method == 'POST':
        inicio = request.form.get('inicio')
        fin = request.form.get('fin')
        
        # Verificar si se han proporcionado valores de inicio y fin
        if inicio and fin:
            # Obtener las coordenadas históricas desde la base de datos
            coordenadas_historicas = obtener_coordenadas_historicas(inicio, fin)
            
            # Pasar los resultados a la plantilla HTML para mostrarlos al usuario
            return render_template('pag2.html', coordenadas_historicas=coordenadas_historicas, inicio=inicio, fin=fin)
        else:
            # Si no se proporcionaron valores de inicio y fin, mostrar un mensaje de error al usuario
            error_message = "Por favor, proporcione valores de inicio y fin."
            return render_template('pag2.html', error_message=error_message)
    
    # Si la solicitud es GET o no se proporcionaron valores de inicio y fin, simplemente renderizar la plantilla
    return render_template('pag2.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
