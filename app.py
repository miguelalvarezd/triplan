from flask import Flask, jsonify, request, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from library.airports_check import find_airports_in_radius

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

################
### CLIENTS  ###
################

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

################
### BOOKINGS ###
################

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

# Get a single booking by its booking code
@app.route('/api/bookings/code/<booking_code>', methods=['GET'])
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

# Get all bookings for a client by DNI
@app.route('/api/bookings/client/<dni>', methods=['GET'])
def get_bookings_client(dni):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE DNI = %s ORDER BY FECHA_INICIO DESC"
        cursor.execute(sql, (dni,))
        bookings = cursor.fetchall()

        if bookings:
            return jsonify({
                'bookings': [
                    {
                        'id': booking[0],
                        'dni': booking[1],
                        'start_date': booking[2],
                        'end_date': booking[3],
                    } for booking in bookings
                ],
                'message': 'Bookings found',
                'success': True
            })
        else:
            return jsonify({'message': 'No bookings found for this client', 'success': False})
    except Exception as ex:
        return jsonify({'message': 'Error fetching bookings', 'success': False, 'error': str(ex)})


# API route for fetching flights
@app.route('/api/flights/booking/<booking_code>', methods=['GET'])
def fetch_flights(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS_AVION WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_code,))
        flights = cursor.fetchall()

        if flights:
            return jsonify({
                'flights': [
                    {
                        'id_vuelo': flight[0],
                        'id_reserva': flight[1],
                        'numero_billete': flight[2],
                        'numero_asiento': flight[3]
                    } for flight in flights
                ],
                'message': 'Flights found',
                'success': True
            })
        else:
            return jsonify({'message': 'No flights found for this booking', 'success': False})
    except Exception as ex:
        return jsonify({'message': 'Error fetching flights', 'success': False, 'error': str(ex)})

# API route for fetching hotels
@app.route('/api/hotels/booking/<booking_code>', methods=['GET'])
def fetch_hotels(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS_HOTEL WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_code,))
        hotels = cursor.fetchall()

        if hotels:
            return jsonify({
                'hotels': [
                    {
                        'id_reserva': hotel[0],
                        'id_hotel': hotel[1],
                        'numero_habitacion': hotel[2]
                    } for hotel in hotels
                ],
                'message': 'Hotels found',
                'success': True
            })
        else:
            return jsonify({'message': 'No hotels found for this booking', 'success': False})
    except Exception as ex:
        return jsonify({'message': 'Error fetching hotels', 'success': False, 'error': str(ex)})

# API route for fetching cars
@app.route('/api/cars/booking/<booking_code>', methods=['GET'])
def fetch_cars(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS_COCHE WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_code,))
        cars = cursor.fetchall()

        if cars:
            return jsonify({
                'cars': [
                    {
                        'id_reserva': car[0],
                        'matricula_coche': car[1]
                    } for car in cars
                ],
                'message': 'Cars found',
                'success': True
            })
        else:
            return jsonify({'message': 'No cars found for this booking', 'success': False})
    except Exception as ex:
        return jsonify({'message': 'Error fetching cars', 'success': False, 'error': str(ex)})
    
# API route for finding cities
@app.route('/api/airports/<city_name>', methods=['GET'])
def fetch_airports(city_name):
    try:
        result, error = find_airports_in_radius(city_name, 500)

        if error:
            return jsonify({'message': error, 'success': False})
        else:
            airports = []
            for airport in result:
                airports.append(airport['code'])

            cursor = conexion.connection.cursor()

            # Dynamically create placeholders
            placeholders = ', '.join(['%s'] * len(airports))

            # Create the SQL query with placeholders
            sql = f"""SELECT T.ID_TRAYECTO, T.DESTINO
                    FROM TRAYECTOS T
                    WHERE T.DESTINO IN ({placeholders})
                    ORDER BY 2;
                """

            # Execute the query with the airports as parameters
            cursor.execute(sql, tuple(airports))
            flights = cursor.fetchall()

            if flights:
                return jsonify({
                    'flights': [
                        {
                            'id_trayecto': flight[0],
                            'destino': flight[1]
                        } for flight in flights
                    ],
                    'message': 'Flights found',
                    'success': True
                })
            else:
                return jsonify({'message': f'No flights found for {city_name}', 'success': False})

    except Exception as ex:
        return jsonify({'message': 'Error fetching flights', 'success': False, 'error': str(ex)})
    
# API route for finding tiers
@app.route('/api/tiers', methods=['GET'])
def fetch_tiers():
    try:
        cursor = conexion.connection.cursor()

        # Create the SQL query with placeholders
        sql = "SELECT TIER, DESCUENTO FROM TIERS ORDER BY DESCUENTO;"

        # Execute the query with the airports as parameters
        cursor.execute(sql)
        tiers = cursor.fetchall()

        if tiers:
            return jsonify({
                'tiers': [
                    {
                        'tier': tier[0],
                        'descuento': tier[1] * 100
                    } for tier in tiers
                ],
                'message': 'Tiers found',
                'success': True
            })
        else:
            return jsonify({'message': 'No tiers found.', 'success': False})

    except Exception as ex:
        return jsonify({'message': 'Error fetching tiers', 'success': False, 'error': str(ex)})
    
# API route for editing tiers
@app.route('/api/tiers', methods=['PUT'])
def update_tier_discount():
    try:
        data = request.json
        tier = data['tier']
        discount = f"{int(data['discount']) / 100}"

        cursor = conexion.connection.cursor()
        sql = "UPDATE TIERS SET DESCUENTO = %s WHERE TIER = %s"
        cursor.execute(sql, (discount, tier))
        conexion.connection.commit()

        return jsonify({'message': 'Tier discount updated successfully.', 'success': True})
    except Exception as ex:
        return jsonify({'message': 'Error updating tier discount.', 'success': False, 'error': str(ex)})
    
# API route for canceling bookings
@app.route('/api/bookings/cancel/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_id,))
        conexion.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': 'No booking found with the provided ID.', 'success': False}), 404

        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE ID_RESERVA = %s AND FECHA_INICIO > DATE_ADD(NOW(), INTERVAL 24 HOUR)"
        cursor.execute(sql, (booking_id,))
        conexion.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': 'Bookings can only be cancelled up to 24 hours before the start date.', 'success': False}), 404


        cursor = conexion.connection.cursor()
        sql = "DELETE FROM RESERVAS WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_id,))
        conexion.connection.commit()

        # Check if a booking was deleted
        if cursor.rowcount == 0:
            return jsonify({'message': 'No booking found with the provided ID.', 'success': False}), 404

        return jsonify({'message': 'Booking cancelled successfully!', 'success': True}), 200
    except Exception as ex:
        return jsonify({'message': 'Error cancelling booking.', 'success': False, 'error': str(ex)}), 500

if __name__ == '__main__':
    app.run(debug=True)
