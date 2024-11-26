from flask import Flask, jsonify, request, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__, static_folder='static')

# Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1075'
app.config['MYSQL_DB'] = 'DB_TRIPLAN'

conexion = MySQL(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

# Client login
@app.route('/api/customers/login', methods=['POST'])
def login_customer():
    try:
        data = request.json
        dni = data.get('dni')
        phone = data.get('phone')

        cursor = conexion.connection.cursor()
        sql = "SELECT DNI, NOMBRE FROM CLIENTES WHERE DNI = %s AND TELEFONO = %s"
        cursor.execute(sql, (dni, phone))
        customer = cursor.fetchone()

        if customer:
            return jsonify({'success': True, 'dni': customer[0], 'name': customer[1]})
        else:
            return jsonify({'success': False, 'message': 'Login failed. Invalid credentials.'})
    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)})


# Register a new customer
@app.route('/api/customers', methods=['POST'])
def register_customer():
    try:
        data = request.json
        dni = data['dni']
        name = data['name']
        phone = data['phone']
        tier = 'BRONZE'

        cursor = conexion.connection.cursor()
        sql = "INSERT INTO CLIENTES (DNI, NOMBRE, TELEFONO, TIER) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (dni, name, phone, tier))
        conexion.connection.commit()

        return jsonify({'message': 'Customer registered successfully', 'success': True})
    except Exception as ex:
        return jsonify({'message': 'Error registering customer', 'success': False, 'error': str(ex)})

# Get a returning customer
@app.route('/api/customers/<dni>', methods=['GET'])
def get_customer(dni):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT DNI, NOMBRE, TELEFONO, TIER FROM CLIENTES WHERE DNI = %s"
        cursor.execute(sql, (dni,))
        customer = cursor.fetchone()

        if customer:
            return jsonify({
                'customer': {
                    'dni': customer[0],
                    'name': customer[1],
                    'phone': customer[2],
                    'tier': customer[3]
                },
                'message': 'Customer found',
                'success': True
            })
        else:
            return jsonify({'message': 'Customer not found', 'success': False})
    except Exception as ex:
        return jsonify({'message': 'Error fetching customer', 'success': False, 'error': str(ex)})

# Create a booking
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.json
        dni = data['dni']
        flight_id = data.get('flight_id')
        hotel_id = data.get('hotel_id')
        car_id = data.get('car_id')

        cursor = conexion.connection.cursor()
        sql = "INSERT INTO RESERVAS (DNI, ID_VUELO, ID_HOTEL, ID_COCHE) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (dni, flight_id, hotel_id, car_id))
        conexion.connection.commit()

        booking_id = cursor.lastrowid
        return jsonify({'message': 'Booking created successfully', 'bookingId': booking_id, 'success': True})
    except Exception as ex:
        return jsonify({'message': 'Error creating booking', 'success': False, 'error': str(ex)})

# Manage booking by booking code
@app.route('/api/bookings/<booking_code>', methods=['GET'])
def get_booking(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_code,))
        booking = cursor.fetchone()

        if booking:
            return jsonify({
                'booking': {
                    'id': booking[0],
                    'dni': booking[1],
                    'start_date': booking[2],
                    'end_date': booking[3],
                },
                'message': 'Booking found',
                'success': True
            })
        else:
            return jsonify({'message': 'Booking not found', 'success': False})
    except Exception as ex:
        return jsonify({'message': 'Error fetching booking', 'success': False, 'error': str(ex)})

if __name__ == '__main__':
    app.run(debug=True)
