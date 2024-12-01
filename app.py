from flask import Flask, jsonify, request, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from library.airports_check import find_airports_in_radius
from library.utils import format_timedelta
from random import choice

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
    
#API route for finding cities
@app.route('/api/flights/route', methods=['GET'])
def fetch_flights_by_cities():
    try:
        # Get query parameters for origin and destination cities
        origin_city = request.args.get('origin')
        destination_city = request.args.get('destination')

        if not origin_city or not destination_city:
            return jsonify({'message': 'Both origin and destination cities are required.', 'success': False}), 400

        # Find airports near the origin city
        origin_airports, origin_error = find_airports_in_radius(origin_city, 500)
        if origin_error:
            return jsonify({'message': origin_error, 'success': False})

        # Find airports near the destination city
        destination_airports, destination_error = find_airports_in_radius(destination_city, 500)
        if destination_error:
            return jsonify({'message': destination_error, 'success': False})

        # Extract airport codes
        origin_codes = [airport['code'] for airport in origin_airports]
        destination_codes = [airport['code'] for airport in destination_airports]

        if not origin_codes or not destination_codes:
            return jsonify({'message': 'No airports found for the given cities.', 'success': False}), 404

        cursor = conexion.connection.cursor()

        # Dynamically create placeholders for origin and destination
        origin_placeholders = ', '.join(['%s'] * len(origin_codes))
        destination_placeholders = ', '.join(['%s'] * len(destination_codes))

        # SQL query to find flights between the origin and destination airports
        sql = f"""
            SELECT T.ID_TRAYECTO, T.ORIGEN, T.DESTINO, T.HORA_SALIDA, T.HORA_LLEGADA
            FROM TRAYECTOS T
            WHERE T.ORIGEN IN ({origin_placeholders}) AND T.DESTINO IN ({destination_placeholders})
            ORDER BY T.DESTINO, T.HORA_SALIDA;
        """

        # Execute the query with both origin and destination airport codes
        cursor.execute(sql, tuple(origin_codes + destination_codes))
        flights = cursor.fetchall()

        if flights:
            return jsonify({
                'flights': [
                    {
                        'id_trayecto': flight[0],
                        'origen': flight[1],
                        'destino': flight[2],
                        'hora_salida': format_timedelta(flight[3]),
                        'hora_llegada': format_timedelta(flight[4])
                    } for flight in flights
                ],
                'message': 'Flights found',
                'success': True
            })
        else:
            return jsonify({'message': 'No flights found between the specified cities.', 'success': False})

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
    

@app.route('/api/flights/check/<id_trayecto>/<date>', methods=['GET'])
def check_flight(id_trayecto, date):
    try:
        cursor = conexion.connection.cursor()
        # Check if flight exists
        sql_check = "SELECT ID_VUELO FROM VUELOS WHERE ID_TRAYECTO = %s AND FECHA_VUELO = %s"
        cursor.execute(sql_check, (id_trayecto, date))
        vuelo = cursor.fetchone()

        if vuelo:
            id_vuelo = vuelo[0]
            # Fetch available seats
            sql_seats = """ SELECT NUMERO_ASIENTO 
                            FROM ASIENTOS 
                            WHERE NUMERO_ASIENTO NOT IN (
                                SELECT NUMERO_ASIENTO FROM RESERVAS_AVION WHERE ID_VUELO = %s)
                        """
            cursor.execute(sql_seats, (id_vuelo, ))
            seats = [row[0] for row in cursor.fetchall()]
            return jsonify({'success': True, 'id_vuelo': id_vuelo, 'available_seats': seats})
        else:
            id_vuelo = None
            # Fetch available seats
            sql_seats = """ SELECT NUMERO_ASIENTO 
                            FROM ASIENTOS
                        """
            cursor.execute(sql_seats)
            seats = [row[0] for row in cursor.fetchall()]
            return jsonify({'success': True, 'id_vuelo': None, 'available_seats': seats, 'message': 'Flight not found. Create a new one.'})
    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)})

@app.route('/api/flights/create', methods=['POST'])
def create_flight():
    try:
        import random

        data = request.json
        id_trayecto = data['id_trayecto']
        date = data['date']

        # Assign a plane
        cursor = conexion.connection.cursor()
        sql_plane = "SELECT MATRICULA_AVION FROM AVIONES"
        cursor.execute(sql_plane)
        planes = cursor.fetchall()

        if not planes:
            return jsonify({'success': False, 'message': 'No planes available.'}), 404

        # Select a random plane
        random_plane = choice(planes)[0]

        # Generate a unique ID_VUELO
        while True:
            id_vuelo = random.randint(1, 99999)
            sql_check_vuelo = "SELECT COUNT(*) FROM VUELOS WHERE ID_VUELO = %s"
            cursor.execute(sql_check_vuelo, (id_vuelo,))
            if cursor.fetchone()[0] == 0:
                break

        # Create new flight
        sql_create = "INSERT INTO VUELOS (ID_VUELO, ID_TRAYECTO, FECHA_VUELO, MATRICULA_AVION) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_create, (id_vuelo, id_trayecto, date, random_plane))
        conexion.connection.commit()

        return jsonify({'success': True, 'message': 'Flight created successfully.', 'plane': random_plane, 'id_vuelo': id_vuelo})
    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)})


@app.route('/api/booking/create', methods=['POST'])
def create_reservation():
    try:
        import random

        data = request.json
        dni = data['DNI']
        fecha_inicio = data['FECHA_INICIO']
        fecha_final = data['FECHA_FINAL']
        id_vuelo = data['ID_VUELO']
        numero_asiento = data['NUMERO_ASIENTO']
        id_hotel = data['ID_HOTEL']
        matricula_coche = data['MATRICULA_COCHE']

        print(id_hotel, matricula_coche)

        cursor = conexion.connection.cursor()

        # Obtain ID_TRAYECTO from the VUELOS table
        sql_get_trayecto = "SELECT ID_TRAYECTO FROM VUELOS WHERE ID_VUELO = %s"
        cursor.execute(sql_get_trayecto, (id_vuelo,))
        id_trayecto_row = cursor.fetchone()

        if not id_trayecto_row:
            return jsonify({'success': False, 'message': 'ID_TRAYECTO not found for the given ID_VUELO.'}), 404

        id_trayecto = id_trayecto_row[0]

        # Generate a unique ID_RESERVA
        while True:
            id_reserva = f"R-{random.randint(1, 99999):05d}"
            sql_check_reserva = "SELECT COUNT(*) FROM RESERVAS WHERE ID_RESERVA = %s"
            cursor.execute(sql_check_reserva, (id_reserva,))
            if cursor.fetchone()[0] == 0:
                break

        # Create new reservation in RESERVAS
        sql_create_reserva = "INSERT INTO RESERVAS (ID_RESERVA, DNI, FECHA_INICIO, FECHA_FINAL) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_create_reserva, (id_reserva, dni, fecha_inicio, fecha_final))

        # Generate a unique NUMERO_BILLETE
        while True:
            numero_billete = f"{id_trayecto}-{random.randint(1000, 9999)}"
            sql_check_billete = "SELECT COUNT(*) FROM RESERVAS_AVION WHERE NUMERO_BILLETE = %s"
            cursor.execute(sql_check_billete, (numero_billete,))
            if cursor.fetchone()[0] == 0:
                break

        # Create new reservation entry in RESERVAS_VUELOS
        sql_create_reserva_vuelo = "INSERT INTO RESERVAS_AVION (ID_RESERVA, ID_VUELO, NUMERO_ASIENTO, NUMERO_BILLETE) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_create_reserva_vuelo, (id_reserva, id_vuelo, numero_asiento, numero_billete))

        # Handle hotel reservation
        if id_hotel is not None:
            # while True:
            #     numero_habitacion = random.randint(12, 12)
            #     sql_check_habitacion = "SELECT COUNT(*) FROM RESERVAS_HOTEL WHERE ID_HOTEL = %s AND NUMERO_HABITACION = %s"
            #     cursor.execute(sql_check_habitacion, (id_hotel, numero_habitacion))
            #     if cursor.fetchone()[0] == 0:
            #         break

            numero_habitacion = 15

            sql_create_reserva_hotel = "INSERT INTO RESERVAS_HOTEL (ID_RESERVA, ID_HOTEL, NUMERO_HABITACION) VALUES (%s, %s, %s)"
            cursor.execute(sql_create_reserva_hotel, (id_reserva, id_hotel, numero_habitacion))

       # Handle car reservation
        if matricula_coche is not None:
            # Check that the car exists
            sql_check_car_exists = """
                SELECT COUNT(*) 
                FROM COCHES 
                WHERE MATRICULA_COCHE = %s
            """
            cursor.execute(sql_check_car_exists, (matricula_coche,))
            if cursor.fetchone()[0] != 1:
                return jsonify({'success': False, 'message': 'Car does not exist.'}), 404

            # # Check if the car is already reserved
            # sql_check_car_reserved = """
            #     SELECT COUNT(*) 
            #     FROM RESERVAS_COCHE 
            #     WHERE MATRICULA_COCHE = %s
            # """
            # cursor.execute(sql_check_car_reserved, (matricula_coche,))
            # if cursor.fetchone()[0] > 0:
            #     return jsonify({'success': False, 'message': 'Car is already reserved.'}), 400

            # Insert the car reservation
            sql_create_reserva_coche = "INSERT INTO RESERVAS_COCHE (ID_RESERVA, MATRICULA_COCHE) VALUES (%s, %s)"
            cursor.execute(sql_create_reserva_coche, (id_reserva, matricula_coche))


        conexion.connection.commit()

        return jsonify({
            'success': True,
            'message': 'Reservation created successfully.',
            'id_reserva': id_reserva,
            'numero_billete': numero_billete,
            'id_vuelo': id_vuelo,
            'fecha_inicio': fecha_inicio,
            'fecha_final': fecha_final,
            'numero_asiento': numero_asiento
        })

    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)})

@app.route('/api/hotels/<city>', methods=['GET'])
def get_hotels(city):
    try:
        cursor = conexion.connection.cursor()
        sql_query = "SELECT ID_HOTEL, NOMBRE_HOTEL, CIUDAD, DIRECCION, PRECIO_POR_NOCHE FROM HOTELES WHERE CIUDAD = %s"
        cursor.execute(sql_query, (city,))
        hotels = cursor.fetchall()

        if hotels:
            hotel_list = [{'id': hotel[0], 'name': hotel[1], 'city': hotel[2], 'price': hotel[4]} for hotel in hotels]
            return jsonify({'success': True, 'hotels': hotel_list})
        else:
            return jsonify({'success': False, 'message': 'No hotels available in this city.'})
    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)})

@app.route('/api/cars/<city>', methods=['GET'])
def get_cars(city):
    try:
        cursor = conexion.connection.cursor()
        sql_query = "SELECT MATRICULA_COCHE, MODELO_COCHE, AEROPUERTO, PRECIO_POR_DIA FROM COCHES WHERE AEROPUERTO = %s"
        cursor.execute(sql_query, (city,))
        cars = cursor.fetchall()

        if cars:
            car_list = [{'id': car[0], 'model': car[1], 'location': car[2], 'price': car[3]} for car in cars]
            return jsonify({'success': True, 'cars': car_list})
        else:
            return jsonify({'success': False, 'message': 'No cars available in this city.'})
    except Exception as ex:
        return jsonify({'success': False, 'message': str(ex)})



if __name__ == '__main__':
    app.run(debug=True)
