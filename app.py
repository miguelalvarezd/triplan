from flask import Flask, jsonify, request, send_from_directory, send_file, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
from library.airports_check import find_airports_in_radius
from library.utils import format_timedelta
from random import choice
import io
import matplotlib.pyplot as plt
from decimal import Decimal
from collections import OrderedDict
import json

app = Flask(__name__, static_folder="static")

# Configure MySQL database
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1075"
app.config["MYSQL_DB"] = "DB_TRIPLAN"

# Custom JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return round(float(obj), 2)
        return super().default(obj)
    
app.json_encoder = CustomJSONEncoder

conexion = MySQL(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")


##############################
#### TEST SENDING PLOTS ######
##############################

# To test sending a dummy plot.
@app.route("/api/plot", methods=["GET"])
def generate_plot():
    plt.figure(figsize=(6, 4))
    plt.plot([1, 2, 3, 4], [10, 20, 25, 30], label="Example Line")
    plt.title("Sample Plot")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()
    plt.grid()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return send_file(buffer, mimetype="image/png")


##############################
########## CLIENTS  ##########
##############################


# Client login
@app.route("/api/customers/login", methods=["POST"])
def login_customer():
    try:
        data = request.json
        dni = data.get("dni")
        phone = data.get("phone")

        cursor = conexion.connection.cursor()
        sql = "SELECT DNI, NOMBRE FROM CLIENTES WHERE DNI = %s AND TELEFONO = %s"
        cursor.execute(sql, (dni, phone))
        customer = cursor.fetchone()

        if customer:
            return jsonify({"success": True, "dni": customer[0], "name": customer[1]})
        else:
            return jsonify(
                {"success": False, "message": "Login failed. Invalid credentials."}
            )
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


# Register a new customer
@app.route("/api/customers", methods=["POST"])
def register_customer():
    try:
        data = request.json
        dni = data["dni"]
        name = data["name"]
        phone = data["phone"]
        tier = "BRONZE"

        cursor = conexion.connection.cursor()
        sql = (
            "INSERT INTO CLIENTES (DNI, NOMBRE, TELEFONO, TIER) VALUES (%s, %s, %s, %s)"
        )
        cursor.execute(sql, (dni, name, phone, tier))
        conexion.connection.commit()

        return jsonify({"message": "Customer registered successfully", "success": True})
    except Exception as ex:
        return jsonify(
            {
                "message": "Error registering customer",
                "success": False,
                "error": str(ex),
            }
        )


# Get data from a returning customer
@app.route("/api/customers/<dni>", methods=["GET"])
def get_customer(dni):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT DNI, NOMBRE, TELEFONO, TIER FROM CLIENTES WHERE DNI = %s"
        cursor.execute(sql, (dni,))
        customer = cursor.fetchone()

        if customer:
            return jsonify(
                {
                    "customer": {
                        "dni": customer[0],
                        "name": customer[1],
                        "phone": customer[2],
                        "tier": customer[3],
                    },
                    "message": "Customer found",
                    "success": True,
                }
            )
        else:
            return jsonify({"message": "Customer not found", "success": False})
    except Exception as ex:
        return jsonify(
            {"message": "Error fetching customer", "success": False, "error": str(ex)}
        )


# Delete a customer account
@app.route("/api/customers/delete/<dni>", methods=["DELETE"])
def delete_customer(dni):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM CLIENTES WHERE DNI = %s"
        cursor.execute(sql, (dni,))
        conexion.connection.commit()
        if cursor.rowcount == 0:
            return jsonify(
                {"message": "No client found with the provided DNI.", "success": False}
            ), 404

        cursor = conexion.connection.cursor()
        sql = "DELETE FROM CLIENTES WHERE DNI = %s"
        cursor.execute(sql, (dni,))
        conexion.connection.commit()

        if cursor.rowcount == 0:
            return jsonify(
                {"message": "No client found with the provided DNI.", "success": False}
            ), 404

        return jsonify(
            {"message": "Account deleted successfully!", "success": True}
        ), 200
    except Exception as ex:
        return jsonify(
            {"message": "Error deleting account.", "success": False, "error": str(ex)}
        ), 500


# Edit a client's tier
@app.route("/api/customers/tier", methods=["PUT"])
def update_tier_client():
    try:
        data = request.json
        tier = data["tier"]
        dni = data["dni"]

        cursor = conexion.connection.cursor()
        sql = "UPDATE CLIENTES SET TIER = %s WHERE DNI = %s"
        cursor.execute(sql, (tier, dni))
        conexion.connection.commit()

        return jsonify({"message": "Tier updated successfully.", "success": True})
    except Exception as ex:
        return jsonify(
            {"message": "Error updating tier.", "success": False, "error": str(ex)}
        )


##############################
######### BOOKINGS  ##########
##############################


# Get a single booking by its booking code
@app.route("/api/bookings/code/<booking_code>", methods=["GET"])
def get_booking(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT R.*, C.NOMBRE 
            FROM RESERVAS R
            JOIN CLIENTES C ON R.DNI = C.DNI
            WHERE R.ID_RESERVA = %s"""
        cursor.execute(sql, (booking_code,))
        booking = cursor.fetchone()

        if booking:
            return jsonify(
                {
                    "booking": {
                        "id": booking[0],
                        "dni": booking[1],
                        "start_date": booking[2],
                        "end_date": booking[3],
                        "name": booking[4],
                    },
                    "message": "Booking found",
                    "success": True,
                }
            )
        else:
            return jsonify({"message": "Booking not found", "success": False})
    except Exception as ex:
        return jsonify(
            {"message": "Error fetching booking", "success": False, "error": str(ex)}
        )


# Get all bookings for a client by DNI
@app.route("/api/bookings/client/<dni>", methods=["GET"])
def get_bookings_client(dni):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE DNI = %s ORDER BY FECHA_INICIO DESC"
        cursor.execute(sql, (dni,))
        bookings = cursor.fetchall()

        if bookings:
            return jsonify(
                {
                    "bookings": [
                        {
                            "id": booking[0],
                            "dni": booking[1],
                            "start_date": booking[2],
                            "end_date": booking[3],
                        }
                        for booking in bookings
                    ],
                    "message": "Bookings found",
                    "success": True,
                }
            )
        else:
            return jsonify(
                {"message": "No bookings found for this client", "success": False}
            )
    except Exception as ex:
        return jsonify(
            {"message": "Error fetching bookings", "success": False, "error": str(ex)}
        )


# Cancel a certain reservation (including flight, hotel and car)
@app.route("/api/bookings/cancel/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_id,))
        conexion.connection.commit()
        if cursor.rowcount == 0:
            return jsonify(
                {"message": "No booking found with the provided ID.", "success": False}
            ), 404

        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM RESERVAS WHERE ID_RESERVA = %s AND FECHA_INICIO > DATE_ADD(NOW(), INTERVAL 24 HOUR)"
        cursor.execute(sql, (booking_id,))
        conexion.connection.commit()
        if cursor.rowcount == 0:
            return jsonify(
                {
                    "message": "Bookings can only be cancelled up to 24 hours before the start date.",
                    "success": False,
                }
            ), 404

        cursor = conexion.connection.cursor()
        sql = "DELETE FROM RESERVAS WHERE ID_RESERVA = %s"
        cursor.execute(sql, (booking_id,))
        conexion.connection.commit()

        if cursor.rowcount == 0:
            return jsonify(
                {"message": "No booking found with the provided ID.", "success": False}
            ), 404

        return jsonify(
            {"message": "Booking cancelled successfully!", "success": True}
        ), 200
    except Exception as ex:
        return jsonify(
            {"message": "Error cancelling booking.", "success": False, "error": str(ex)}
        ), 500


# Create a new reservation (with flight, hotel and car, if applicable)
@app.route("/api/bookings/create", methods=["POST"])
def create_reservation():
    try:
        import random

        data = request.json
        dni = data["DNI"]
        fecha_inicio = data["FECHA_INICIO"]
        fecha_final = data["FECHA_FINAL"]
        id_vuelo = data["ID_VUELO"]
        numero_asiento = data["NUMERO_ASIENTO"]
        id_hotel = data["ID_HOTEL"]
        matricula_coche = data["MATRICULA_COCHE"]

        print(id_hotel, matricula_coche)

        cursor = conexion.connection.cursor()

        # Obtain ID_TRAYECTO from the VUELOS table
        sql_get_trayecto = "SELECT ID_TRAYECTO FROM VUELOS WHERE ID_VUELO = %s"
        cursor.execute(sql_get_trayecto, (id_vuelo,))
        id_trayecto_row = cursor.fetchone()

        if not id_trayecto_row:
            return jsonify(
                {
                    "success": False,
                    "message": "ID_TRAYECTO not found for the given ID_VUELO.",
                }
            ), 404

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
            sql_check_billete = (
                "SELECT COUNT(*) FROM RESERVAS_AVION WHERE NUMERO_BILLETE = %s"
            )
            cursor.execute(sql_check_billete, (numero_billete,))
            if cursor.fetchone()[0] == 0:
                break

        # Create new reservation entry in RESERVAS_VUELOS
        sql_create_reserva_vuelo = "INSERT INTO RESERVAS_AVION (ID_RESERVA, ID_VUELO, NUMERO_ASIENTO, NUMERO_BILLETE) VALUES (%s, %s, %s, %s)"
        cursor.execute(
            sql_create_reserva_vuelo,
            (id_reserva, id_vuelo, numero_asiento, numero_billete),
        )

        # Handle hotel reservation
        if id_hotel is not None:
            while True:
                # First get the hotel's NUMERO_HABITACIONES
                sql_check_capacity = (
                    "SELECT HABITACIONES_TOTALES FROM HOTELES WHERE ID_HOTEL = %s"
                )
                cursor.execute(sql_check_capacity, (id_hotel,))
                max_rooms_tuple = cursor.fetchone()

                max_rooms = max_rooms_tuple[0] if max_rooms_tuple else 0  # Handle None case

                # Generate a random room number
                numero_habitacion = random.randint(1, int(max_rooms))

                if not max_rooms:
                    continue

                # Check if the room is already reserved
                sql_check_reservas = """
                    SELECT COUNT(*)
                    FROM RESERVAS_HOTEL RH
                    JOIN RESERVAS R ON RH.ID_RESERVA = R.ID_RESERVA
                    WHERE RH.ID_HOTEL = %s
                    AND RH.NUMERO_HABITACION = %s
                    AND (
                            (%s BETWEEN R.FECHA_INICIO AND R.FECHA_FINAL) OR
                            (%s BETWEEN R.FECHA_INICIO AND R.FECHA_FINAL) OR
                            (R.FECHA_INICIO BETWEEN %s AND %s) OR
                            (R.FECHA_FINAL BETWEEN %s AND %s)
                        )
                """
                cursor.execute(
                    sql_check_reservas,
                    (
                        id_hotel,
                        numero_habitacion,
                        fecha_inicio,
                        fecha_final,
                        fecha_inicio,
                        fecha_final,
                        fecha_inicio,
                        fecha_final,
                    ),
                )
                overlap_count = cursor.fetchone()[0]

                if overlap_count > 0:
                    continue

                # Check if the room exists in the HABITACIONES table
                sql_check_habitacion = "SELECT COUNT(*) FROM HABITACIONES WHERE ID_HOTEL = %s AND NUMERO_HABITACION = %s"
                cursor.execute(sql_check_habitacion, (id_hotel, numero_habitacion))
                if cursor.fetchone()[0] == 0:
                    # Room does not exist in HABITACIONES, create it
                    # Generate random values for new room attributes
                    precio_extra = random.randint(
                        50, 200
                    )

                    sql_room_type = "SELECT DISTINCT TIPO_HABITACION FROM HABITACIONES;"
                    cursor.execute(sql_room_type)

                    tipos_disponibles = [row[0] for row in cursor.fetchall()]

                    # tipos_disponibles = [
                    #     "DOUBLE",
                    #     "SUITE",
                    #     "SINGLE",
                    #     "DELUXE",
                    #     "FAMILY",
                    # ]  # Adjust available types as necessary
                    tipo_habitacion = random.choice(tipos_disponibles)

                    # Insert new room into HABITACIONES
                    sql_create_habitacion = """
                        INSERT INTO HABITACIONES (ID_HOTEL, NUMERO_HABITACION, PRECIO_EXTRA, TIPO_HABITACION)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(
                        sql_create_habitacion,
                        (id_hotel, numero_habitacion, precio_extra, tipo_habitacion),
                    )

                # Room is valid and available, exit loop
                break

            # Create a reservation for the room
            sql_create_reserva_hotel = """
                INSERT INTO RESERVAS_HOTEL (ID_RESERVA, ID_HOTEL, NUMERO_HABITACION) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(
                sql_create_reserva_hotel, (id_reserva, id_hotel, numero_habitacion)
            )

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
                return jsonify(
                    {"success": False, "message": "Car does not exist."}
                ), 404

            # Check if the car is already reserved for the given dates
            sql_check_car_reserved = """
                SELECT COUNT(*) 
                FROM RESERVAS_COCHE RC
                JOIN RESERVAS R ON RC.ID_RESERVA = R.ID_RESERVA
                WHERE RC.MATRICULA_COCHE = %s
                AND (
                        (%s BETWEEN R.FECHA_INICIO AND R.FECHA_FINAL) OR
                        (%s BETWEEN R.FECHA_INICIO AND R.FECHA_FINAL) OR
                        (R.FECHA_INICIO BETWEEN %s AND %s) OR
                        (R.FECHA_FINAL BETWEEN %s AND %s)
                    )
            """
            cursor.execute(
                sql_check_car_reserved,
                (
                    matricula_coche,
                    fecha_inicio,
                    fecha_final,
                    fecha_inicio,
                    fecha_final,
                    fecha_inicio,
                    fecha_final,
                ),
            )
            if cursor.fetchone()[0] > 0:
                return jsonify(
                    {
                        "success": False,
                        "message": "Car is already reserved for the selected dates.",
                    }
                ), 400

            # Insert the car reservation
            sql_create_reserva_coche = "INSERT INTO RESERVAS_COCHE (ID_RESERVA, MATRICULA_COCHE) VALUES (%s, %s)"
            cursor.execute(sql_create_reserva_coche, (id_reserva, matricula_coche))

        conexion.connection.commit()

        return jsonify(
            {
                "success": True,
                "message": "Reservation created successfully.",
                "id_reserva": id_reserva,
                "numero_billete": numero_billete,
                "id_vuelo": id_vuelo,
                "fecha_inicio": fecha_inicio,
                "fecha_final": fecha_final,
                "numero_asiento": numero_asiento,
            }
        )

    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


##############################
########## FLIGHTS  ##########
##############################


# Obtain flights associated to a reservation
@app.route("/api/flights/booking/<booking_code>", methods=["GET"])
def fetch_flights(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT RA.ID_VUELO, RA.ID_RESERVA, RA.NUMERO_BILLETE, RA.NUMERO_ASIENTO, A.MODELO_AVION, T.ID_TRAYECTO, T.ORIGEN, T.DESTINO
            FROM RESERVAS_AVION RA 
            JOIN VUELOS V ON RA.ID_VUELO = V.ID_VUELO
            JOIN AVIONES A ON V.MATRICULA_AVION = A.MATRICULA_AVION
            JOIN TRAYECTOS T ON V.ID_TRAYECTO = T.ID_TRAYECTO
            WHERE RA.ID_RESERVA = %s"""
        cursor.execute(sql, (booking_code,))
        flights = cursor.fetchall()

        if flights:
            return jsonify(
                {
                    "flights": [
                        {
                            "id_vuelo": flight[0],
                            "id_reserva": flight[1],
                            "numero_billete": flight[2],
                            "numero_asiento": flight[3],
                            "modelo_avion": flight[4],
                            "id_trayecto": flight[5],
                            "origen": flight[6],
                            "destino": flight[7],
                        }
                        for flight in flights
                    ],
                    "message": "Flights found",
                    "success": True,
                }
            )
        else:
            return jsonify(
                {"message": "No flights found for this booking", "success": False}
            )
    except Exception as ex:
        return jsonify(
            {"message": "Error fetching flights", "success": False, "error": str(ex)}
        )


# Find airport codes in a 200km radius of a city
@app.route("/api/flights/route", methods=["GET"])
def fetch_flights_by_cities():
    try:
        origin_city = request.args.get("origin")
        destination_city = request.args.get("destination")

        if not origin_city or not destination_city:
            return jsonify(
                {
                    "message": "Both origin and destination cities are required.",
                    "success": False,
                }
            ), 400

        # Find airports near the origin city
        origin_airports, origin_error = find_airports_in_radius(origin_city, 500)
        if origin_error:
            return jsonify({"message": origin_error, "success": False})

        # Find airports near the destination city
        destination_airports, destination_error = find_airports_in_radius(
            destination_city, 500
        )
        if destination_error:
            return jsonify({"message": destination_error, "success": False})

        # Extract airport codes
        origin_codes = [airport["code"] for airport in origin_airports]
        destination_codes = [airport["code"] for airport in destination_airports]

        if not origin_codes or not destination_codes:
            return jsonify(
                {"message": "No airports found for the given cities.", "success": False}
            ), 404

        cursor = conexion.connection.cursor()

        origin_placeholders = ", ".join(["%s"] * len(origin_codes))
        destination_placeholders = ", ".join(["%s"] * len(destination_codes))

        sql = f"""
            SELECT T.ID_TRAYECTO, T.ORIGEN, T.DESTINO, T.HORA_SALIDA, T.HORA_LLEGADA
            FROM TRAYECTOS T
            WHERE T.ORIGEN IN ({origin_placeholders}) AND T.DESTINO IN ({destination_placeholders})
            ORDER BY T.DESTINO, T.HORA_SALIDA;
        """

        cursor.execute(sql, tuple(origin_codes + destination_codes))
        flights = cursor.fetchall()

        if flights:
            return jsonify(
                {
                    "flights": [
                        {
                            "id_trayecto": flight[0],
                            "origen": flight[1],
                            "destino": flight[2],
                            "hora_salida": format_timedelta(flight[3]),
                            "hora_llegada": format_timedelta(flight[4]),
                        }
                        for flight in flights
                    ],
                    "message": "Flights found",
                    "success": True,
                }
            )
        else:
            return jsonify(
                {
                    "message": "No flights found between the specified cities.",
                    "success": False,
                }
            )

    except Exception as ex:
        return jsonify(
            {"message": "Error fetching flights", "success": False, "error": str(ex)}
        )


# Obtain between two ariports
@app.route("/api/flights/between/<origen>/<destino>", methods=["GET"])
def check_flight_between(origen, destino):
    try:
        cursor = conexion.connection.cursor()

        sql = """
            SELECT T.ID_TRAYECTO, T.ORIGEN, T.DESTINO, T.HORA_SALIDA, T.HORA_LLEGADA
            FROM TRAYECTOS T
            WHERE T.ORIGEN = %s AND T.DESTINO = %s
            ORDER BY T.DESTINO, T.HORA_SALIDA;
        """
        cursor.execute(sql, (origen, destino))
        flights = cursor.fetchall()

        if flights:
            return jsonify(
                {
                    "flights": [
                        {
                            "id_trayecto": flight[0],
                            "origen": flight[1],
                            "destino": flight[2],
                            "hora_salida": format_timedelta(flight[3]),
                            "hora_llegada": format_timedelta(flight[4]),
                        }
                        for flight in flights
                    ],
                    "message": "Flights found",
                    "success": True,
                }
            )
        else:
            return jsonify(
                {
                    "message": "No flights found between the specified cities.",
                    "success": False,
                }
            )
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


# Obtain flights following a route on a certain date
@app.route("/api/flights/check/<id_trayecto>/<date>", methods=["GET"])
def check_flight(id_trayecto, date):
    try:
        cursor = conexion.connection.cursor()

        sql_check = (
            "SELECT ID_VUELO FROM VUELOS WHERE ID_TRAYECTO = %s AND FECHA_VUELO = %s"
        )
        cursor.execute(sql_check, (id_trayecto, date))
        vuelo = cursor.fetchone()

        if vuelo:
            id_vuelo = vuelo[0]

            sql_seats = """ SELECT NUMERO_ASIENTO 
                            FROM ASIENTOS 
                            WHERE NUMERO_ASIENTO NOT IN (
                                SELECT NUMERO_ASIENTO FROM RESERVAS_AVION WHERE ID_VUELO = %s)
                        """
            cursor.execute(sql_seats, (id_vuelo,))
            seats = [row[0] for row in cursor.fetchall()]
            return jsonify(
                {"success": True, "id_vuelo": id_vuelo, "available_seats": seats}
            )
        else:
            id_vuelo = None

            sql_seats = """ SELECT NUMERO_ASIENTO 
                            FROM ASIENTOS
                        """
            cursor.execute(sql_seats)
            seats = [row[0] for row in cursor.fetchall()]
            return jsonify(
                {
                    "success": True,
                    "id_vuelo": None,
                    "available_seats": seats,
                    "message": "Flight not found. Create a new one.",
                }
            )
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


# Create a new flight
@app.route("/api/flights/create", methods=["POST"])
def create_flight():
    try:
        import random

        data = request.json
        id_trayecto = data["id_trayecto"]
        date = data["date"]

        cursor = conexion.connection.cursor()
        sql_plane = "SELECT MATRICULA_AVION FROM AVIONES"
        cursor.execute(sql_plane)
        planes = cursor.fetchall()

        if not planes:
            return jsonify({"success": False, "message": "No planes available."}), 404

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

        return jsonify(
            {
                "success": True,
                "message": "Flight created successfully.",
                "plane": random_plane,
                "id_vuelo": id_vuelo,
            }
        )
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


# Add a flight to a certain, already existing reservation
@app.route("/api/flights/booking/add", methods=["POST"])
def add_flight():
    try:
        import random

        data = request.json
        id_reserva = data["ID_RESERVA"]
        id_vuelo = data["ID_VUELO"]
        numero_asiento = data["NUMERO_ASIENTO"]

        cursor = conexion.connection.cursor()

        # Obtain ID_TRAYECTO from the VUELOS table
        sql_get_trayecto = "SELECT ID_TRAYECTO FROM VUELOS WHERE ID_VUELO = %s"
        cursor.execute(sql_get_trayecto, (id_vuelo,))
        id_trayecto_row = cursor.fetchone()

        if not id_trayecto_row:
            return jsonify(
                {
                    "success": False,
                    "message": "ID_TRAYECTO not found for the given ID_VUELO.",
                }
            ), 404

        id_trayecto = id_trayecto_row[0]

        # Generate a unique NUMERO_BILLETE
        while True:
            numero_billete = f"{id_trayecto}-{random.randint(1000, 9999)}"
            sql_check_billete = (
                "SELECT COUNT(*) FROM RESERVAS_AVION WHERE NUMERO_BILLETE = %s"
            )
            cursor.execute(sql_check_billete, (numero_billete,))
            if cursor.fetchone()[0] == 0:
                break

        # Create new reservation entry in RESERVAS_VUELOS
        sql_create_reserva_vuelo = "INSERT INTO RESERVAS_AVION (ID_RESERVA, ID_VUELO, NUMERO_ASIENTO, NUMERO_BILLETE) VALUES (%s, %s, %s, %s)"
        cursor.execute(
            sql_create_reserva_vuelo,
            (id_reserva, id_vuelo, numero_asiento, numero_billete),
        )

        conexion.connection.commit()

        return jsonify(
            {
                "success": True,
                "message": "Reservation created successfully.",
                "id_reserva": id_reserva,
                "numero_billete": numero_billete,
                "id_vuelo": id_vuelo,
                "numero_asiento": numero_asiento,
            }
        )

    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


##############################
##########  HOTELS  ##########
##############################


# Obtain hotels associated to a reservation
@app.route("/api/hotels/booking/<booking_code>", methods=["GET"])
def fetch_hotels(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT RH.ID_RESERVA, RH.ID_HOTEL, RH.NUMERO_HABITACION , H.NOMBRE_HOTEL, H.DIRECCION, H.CIUDAD, HA.TIPO_HABITACION
            FROM RESERVAS_HOTEL RH
            JOIN HOTELES H ON RH.ID_HOTEL = H.ID_HOTEL
            JOIN HABITACIONES HA ON (RH.NUMERO_HABITACION = HA.NUMERO_HABITACION AND RH.ID_HOTEL = HA.ID_HOTEL)
            WHERE RH.ID_RESERVA = %s"""
        cursor.execute(sql, (booking_code,))
        hotels = cursor.fetchall()

        if hotels:
            return jsonify(
                {
                    "hotels": [
                        {
                            "id_reserva": hotel[0],
                            "id_hotel": hotel[1],
                            "numero_habitacion": hotel[2],
                            "nombre_hotel": hotel[3],
                            "direccion": hotel[4],
                            "ciudad": hotel[5],
                            "tipo_habitacion": hotel[6],
                        }
                        for hotel in hotels
                    ],
                    "message": "Hotels found",
                    "success": True,
                }
            )
        else:
            return jsonify(
                {"message": "No hotels found for this booking", "success": False}
            )
    except Exception as ex:
        return jsonify(
            {"message": "Error fetching hotels", "success": False, "error": str(ex)}
        )


# Obtain all hotels in a city
@app.route("/api/hotels/<city>", methods=["GET"])
def get_hotels(city):
    try:
        cursor = conexion.connection.cursor()
        sql_query = "SELECT ID_HOTEL, NOMBRE_HOTEL, CIUDAD, DIRECCION, PRECIO_POR_NOCHE FROM HOTELES WHERE CIUDAD = %s"
        cursor.execute(sql_query, (city,))
        hotels = cursor.fetchall()

        if hotels:
            hotel_list = [
                {"id": hotel[0], "name": hotel[1], "city": hotel[2], "price": hotel[4]}
                for hotel in hotels
            ]
            return jsonify({"success": True, "hotels": hotel_list})
        else:
            return jsonify(
                {"success": False, "message": "No hotels available in this city."}
            )
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


##############################
##########   CARS   ##########
##############################


# Obtain cars associated to a reservation
@app.route("/api/cars/booking/<booking_code>", methods=["GET"])
def fetch_cars(booking_code):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT RC.ID_RESERVA, RC.MATRICULA_COCHE, C.MODELO_COCHE
            FROM RESERVAS_COCHE RC
            JOIN COCHES C ON RC.MATRICULA_COCHE = C.MATRICULA_COCHE
            WHERE RC.ID_RESERVA = %s"""
        cursor.execute(sql, (booking_code,))
        cars = cursor.fetchall()

        if cars:
            return jsonify(
                {
                    "cars": [
                        {
                            "id_reserva": car[0],
                            "matricula_coche": car[1],
                            "modelo_coche": car[2],
                        }
                        for car in cars
                    ],
                    "message": "Cars found",
                    "success": True,
                }
            )
        else:
            return jsonify(
                {"message": "No cars found for this booking", "success": False}
            )
    except Exception as ex:
        return jsonify(
            {"message": "Error fetching cars", "success": False, "error": str(ex)}
        )


# Obtain all cars in a city
@app.route("/api/cars/<city>", methods=["GET"])
def get_cars(city):
    try:
        cursor = conexion.connection.cursor()
        sql_query = "SELECT MATRICULA_COCHE, MODELO_COCHE, AEROPUERTO, PRECIO_POR_DIA FROM COCHES WHERE AEROPUERTO = %s"
        cursor.execute(sql_query, (city,))
        cars = cursor.fetchall()

        if cars:
            car_list = [
                {"id": car[0], "model": car[1], "location": car[2], "price": car[3]}
                for car in cars
            ]
            return jsonify({"success": True, "cars": car_list})
        else:
            return jsonify(
                {"success": False, "message": "No cars available in this city."}
            )
    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)})


##############################
##########  TIERS   ##########
##############################


# Obtain all tiers available
@app.route("/api/tiers", methods=["GET"])
def fetch_tiers():
    try:
        cursor = conexion.connection.cursor()

        sql = "SELECT TIER, DESCUENTO FROM TIERS ORDER BY DESCUENTO;"

        cursor.execute(sql)
        tiers = cursor.fetchall()

        if tiers:
            return jsonify(
                {
                    "tiers": [
                        {"tier": tier[0], "descuento": tier[1] * 100} for tier in tiers
                    ],
                    "message": "Tiers found",
                    "success": True,
                }
            )
        else:
            return jsonify({"message": "No tiers found.", "success": False})

    except Exception as ex:
        return jsonify(
            {"message": "Error fetching tiers", "success": False, "error": str(ex)}
        )


# Edit the discount on a certain tier
@app.route("/api/tiers/edit", methods=["PUT"])
def update_tier_discount():
    try:
        data = request.json
        tier = data["tier"]
        discount = f"{int(data['discount']) / 100}"

        cursor = conexion.connection.cursor()
        sql = "UPDATE TIERS SET DESCUENTO = %s WHERE TIER = %s"
        cursor.execute(sql, (discount, tier))
        conexion.connection.commit()

        return jsonify(
            {"message": "Tier discount updated successfully.", "success": True}
        )
    except Exception as ex:
        return jsonify(
            {
                "message": "Error updating tier discount.",
                "success": False,
                "error": str(ex),
            }
        )


##############################
######## TOTAL PRICE #########
##############################


# Calculate the total price of a reservation
@app.route("/api/calculate_price", methods=["POST"])
def calculate_price():
    try:
        data = request.json
        dni = data.get("DNI")
        id_trayecto = data.get("ID_TRAYECTO")
        id_trayecto_vuelta = data.get("ID_TRAYECTO_VUELTA")
        numero_asiento = data.get("NUMERO_ASIENTO")
        numero_asiento_vuelta = data.get("NUMERO_ASIENTO_VUELTA")
        id_hotel = data.get("ID_HOTEL")
        matricula_coche = data.get("MATRICULA_COCHE")

        cursor = conexion.connection.cursor()

        query_parts = []
        params = []

        if id_trayecto:
            query_parts.append(
                "(SELECT T.PRECIO_TRAYECTO FROM TRAYECTOS T WHERE T.ID_TRAYECTO = %s)"
            )
            params.append(id_trayecto)

        if numero_asiento:
            query_parts.append(
                "(SELECT A.PRECIO_EXTRA FROM ASIENTOS A WHERE A.NUMERO_ASIENTO = %s)"
            )
            params.extend([numero_asiento])

        if id_trayecto_vuelta:
            query_parts.append(
                "(SELECT T2.PRECIO_TRAYECTO FROM TRAYECTOS T2 WHERE T2.ID_TRAYECTO = %s)"
            )
            params.append(id_trayecto_vuelta)

        if numero_asiento_vuelta:
            query_parts.append(
                "(SELECT A2.PRECIO_EXTRA FROM ASIENTOS A2 WHERE A2.NUMERO_ASIENTO = %s)"
            )
            params.extend([numero_asiento_vuelta])

        if id_hotel:
            query_parts.append(
                "(SELECT H.PRECIO_POR_NOCHE FROM HOTELES H WHERE H.ID_HOTEL = %s)"
            )
            params.append(id_hotel)

        if matricula_coche:
            query_parts.append(
                "(SELECT C.PRECIO_POR_DIA FROM COCHES C WHERE C.MATRICULA_COCHE = %s)"
            )
            params.append(matricula_coche)

        total_query = " + ".join(query_parts)

        tier_discount_query = (
            "SELECT (%s) * (1 - TI.DESCUENTO) AS TOTAL_PRICE "
            "FROM CLIENTES CL "
            "JOIN TIERS TI ON CL.TIER = TI.TIER WHERE CL.DNI = %s"
        )

        final_query = tier_discount_query % (total_query, "%s")
        params.append(dni)

        cursor.execute(final_query, params)
        result = cursor.fetchone()

        if result:
            total_price = result[0]
        else:
            total_price = 0

        return jsonify({"success": True, "totalPrice": total_price})

    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 400


##############################
##########  REPORTS ##########
##############################


@app.route("/api/reports/<report_type>", methods=["GET"])
def generate_report(report_type):
    try:
        cursor = conexion.connection.cursor()

        queries = {
            "popular-routes": """
                SELECT T.ORIGEN AS Origin, T.DESTINO AS Destination, COUNT(V.ID_VUELO) AS `Total Flights`,
                AVG(T.PRECIO_TRAYECTO) AS `Average Price (€)`
                FROM TRAYECTOS T
                JOIN VUELOS V ON T.ID_TRAYECTO = V.ID_TRAYECTO
                WHERE V.FECHA_VUELO BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE()
                GROUP BY T.ORIGEN, T.DESTINO
                ORDER BY `Total Flights` DESC;
            """,
            "plane-models": """
                SELECT TRAYECTOS.ID_TRAYECTO AS `Route ID`, TRAYECTOS.ORIGEN AS `Origin`, TRAYECTOS.DESTINO AS `Destination`,
                COUNT(RESERVAS_AVION.NUMERO_BILLETE) AS `Total Tickets Sold`,
                SUM(TRAYECTOS.PRECIO_TRAYECTO + ASIENTOS.PRECIO_EXTRA) AS `Total Revenue (€)`
                FROM TRAYECTOS
                JOIN VUELOS ON TRAYECTOS.ID_TRAYECTO = VUELOS.ID_TRAYECTO
                JOIN RESERVAS_AVION ON VUELOS.ID_VUELO = RESERVAS_AVION.ID_VUELO
                JOIN ASIENTOS ON RESERVAS_AVION.NUMERO_ASIENTO = ASIENTOS.NUMERO_ASIENTO
                GROUP BY TRAYECTOS.ID_TRAYECTO, TRAYECTOS.ORIGEN, TRAYECTOS.DESTINO
                HAVING `Total Revenue (€)` > 1000
                ORDER BY `Total Revenue (€)` DESC;
            """,
            "high-reservation-clients": """
                SELECT CLIENTES.TIER AS `Tier`, CLIENTES.DNI AS `DNI`, CLIENTES.NOMBRE AS `NAME`,
                COUNT(RESERVAS.ID_RESERVA) AS `Number of Reservations`
                FROM CLIENTES
                JOIN RESERVAS ON CLIENTES.DNI = RESERVAS.DNI
                WHERE RESERVAS.FECHA_INICIO >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                GROUP BY CLIENTES.DNI, CLIENTES.TIER, CLIENTES.NOMBRE
                HAVING `Number of Reservations` > 3
                ORDER BY `Number of Reservations` DESC;
            """,
            "avg-plane-income": """
                SELECT MODELOS_AVION.FABRICANTE AS `Manufacturer`, MODELOS_AVION.MODELO_AVION AS `Airplane Model`,
                COALESCE(AVG(INGRESOS.INGRESOS_TOTALES), 0) AS `Average Revenue (€)`
                FROM MODELOS_AVION
                LEFT JOIN AVIONES ON MODELOS_AVION.MODELO_AVION = AVIONES.MODELO_AVION
                LEFT JOIN VUELOS ON AVIONES.MATRICULA_AVION = VUELOS.MATRICULA_AVION
                LEFT JOIN (
                    SELECT RESERVAS_AVION.ID_VUELO,
                    SUM(COALESCE(TRAYECTOS.PRECIO_TRAYECTO, 0) + COALESCE(ASIENTOS.PRECIO_EXTRA, 0)) AS INGRESOS_TOTALES
                    FROM RESERVAS_AVION
                    LEFT JOIN TRAYECTOS ON RESERVAS_AVION.ID_VUELO = TRAYECTOS.ID_TRAYECTO
                    LEFT JOIN ASIENTOS ON RESERVAS_AVION.NUMERO_ASIENTO = ASIENTOS.NUMERO_ASIENTO
                    GROUP BY RESERVAS_AVION.ID_VUELO
                ) AS INGRESOS ON VUELOS.ID_VUELO = INGRESOS.ID_VUELO
                GROUP BY MODELOS_AVION.FABRICANTE, MODELOS_AVION.MODELO_AVION
                HAVING `Average Revenue (€)` >= 0;
            """,
        }

        if report_type not in queries:
            return jsonify({"success": False, "message": "Invalid report type."}), 400

        cursor.execute(queries[report_type])
        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]

        report = [
            OrderedDict(zip(columns, row)) for row in rows      # To maintain ordered columns
        ]

        return Response(json.dumps({"success": True, "report": report}, cls=CustomJSONEncoder),
                        mimetype="application/json", status=200)

    except Exception as ex:
        return jsonify({"success": False, "message": str(ex)}), 500


##############################
##########   MAIN   ##########
##############################

# Start the REST-API and Flask Server
if __name__ == "__main__":
    app.run(debug=True)
