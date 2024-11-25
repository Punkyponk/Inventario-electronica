from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "inventario_secreto"

# Datos de estudiantes para login
estudiantes = {
    "21590125": "Elias Enrique Garcia Reyes",
    "21590123": "Aldo Galvan Monroy",
    "21590404": "Colorado Trejo Braulio",
    "21590132": "Josué Misael Velázquez Primero",
    "21590121": "Jesus David Chávez Rodríguez"
}

# Inventario de objetos electrónicos
inventario =  [
    {"id": 4723, "nombre": "Osciloscopio Digital", "descripcion": "Osciloscopio digital de 200 MHz con pantalla LCD y múltiples canales de entrada.", "cantidad": 5, "precio": 1200, "estado": "bueno"},
    {"id": 1589, "nombre": "Fuente de Poder Regulada", "descripcion": "Fuente de poder ajustable de 30V y 5A, ideal para pruebas de circuitos electrónicos.", "cantidad": 10, "precio": 250, "estado": "bueno"},
    {"id": 6341, "nombre": "Multímetro Digital", "descripcion": "Multímetro digital de 6000 cuentas, con mediciones de voltaje, corriente y resistencia.", "cantidad": 25, "precio": 40, "estado": "bueno"},
    {"id": 9075, "nombre": "Generador de Señales", "descripcion": "Generador de señales de frecuencia variable de hasta 50 MHz, ideal para pruebas y prototipos.", "cantidad": 8, "precio": 400, "estado": "bueno"},
    {"id": 2846, "nombre": "Estación de Soldado", "descripcion": "Estación de soldado con temperatura ajustable y punta de alta precisión para trabajos delicados.", "cantidad": 12, "precio": 75, "estado": "bueno"},
    {"id": 7310, "nombre": "Analizador de Espectro", "descripcion": "Analizador de espectro portátil con rango de 9 kHz a 6 GHz para pruebas RF.", "cantidad": 3, "precio": 2500, "estado": "bueno"},
    {"id": 4952, "nombre": "Pinza Amperimétrica", "descripcion": "Pinza amperimétrica digital con medición de corriente alterna y continua, hasta 1000 A.", "cantidad": 15, "precio": 150, "estado": "bueno"},
    {"id": 8604, "nombre": "Rebajadora de Placas PCB", "descripcion": "Rebajadora de placas de circuito impreso, con control de velocidad y alta precisión.", "cantidad": 7, "precio": 650, "estado": "bueno"},
    {"id": 3127, "nombre": "Soldador de Aire Caliente", "descripcion": "Soldador de aire caliente para desoldar componentes SMD y reparaciones de placa.", "cantidad": 10, "precio": 120, "estado": "bueno"},
    {"id": 5789, "nombre": "Probador de Componentes Electrónicos", "descripcion": "Probador automático de componentes electrónicos con medición de diodos, transistores y resistencias.", "cantidad": 20, "precio": 55, "estado": "bueno"}
]

# Productos retirados y en mal estado
productos_prestados = []
productos_malos = []

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    numero_control = request.form['numero_control']
    nombre = request.form['nombre']
    
    if numero_control in estudiantes and estudiantes[numero_control] == nombre:
        session['usuario'] = nombre
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Número de control o nombre incorrectos.")

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/inventario')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', 
                           inventario=inventario, 
                           productos_prestados=productos_prestados,
                           productos_malos=productos_malos)

@app.route('/agregar', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    cantidad = int(request.form['cantidad'])
    estado = request.form['estado']
    nuevo_id = max([producto['id'] for producto in inventario]) + 1 if inventario else 1

    inventario.append({
        "id": nuevo_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "cantidad": cantidad,
        "estado": estado
    })
    return redirect(url_for('index'))

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    cantidad_eliminar = int(request.form['cantidad_eliminar'])
    producto = next((prod for prod in inventario if prod['id'] == id), None)
    
    if producto:
        if producto['cantidad'] >= cantidad_eliminar:
            producto['cantidad'] -= cantidad_eliminar
    return redirect(url_for('index'))

@app.route('/retirar', methods=['POST'])
def retirar_producto():
    id_producto = int(request.form['id_producto'])
    producto = next((prod for prod in inventario if prod['id'] == id_producto), None)

    if producto and producto['cantidad'] > 0:
        producto['cantidad'] -= 1
        producto_retirado = producto.copy()
        producto_retirado['fecha_retiro'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        productos_prestados.append(producto_retirado)
    
    return redirect(url_for('index'))

@app.route('/devolver_producto/<int:id>', methods=['POST'])
def devolver_producto(id):
    estado_devuelto = request.form['estado_devuelto']
    producto = next((prod for prod in productos_prestados if prod['id'] == id), None)

    if producto:
        if estado_devuelto == "malo":
            if producto not in productos_malos:
                productos_malos.append(producto)
        else:
            inventario_producto = next((prod for prod in inventario if prod['id'] == producto['id']), None)
            if inventario_producto:
                inventario_producto['cantidad'] += 1

        productos_prestados.remove(producto)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
