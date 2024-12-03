import mysql.connector
from mysql.connector import Error
from prettytable import PrettyTable

def connect_to_database():
    try:
        password = input("Introduce la contraseña de MySQL: ")
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password,
            database='DB_TRIPLAN'
        )
        if connection.is_connected():
            print("\nConexión exitosa a MySQL.")
            return connection
    except Error as e:
        print(f"\nError al conectar a MySQL: {e}")
        return None

def show_menu():
    print("\n--- Menú Principal ---")
    print("1. Listar Reservas")
    print("2. Actualizar")
    print("3. Eliminar")
    print("4. Buscar Estadísticas")
    print("5. Salir")

def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results, cursor.column_names
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return None, None

def display_results(results, column_names):
    if results:
        table = PrettyTable()
        table.field_names = column_names
        for row in results:
            table.add_row(row)
        print(table)
    else:
        print("No se encontraron resultados.")

def list_reservations():
    print("\n--- Listar Reservas ---")

    print("1. Mostrar solo reservas")
    print("2. Mostrar reservas con hotel, avión o coche")
    display_choice = input("\nSelecciona una opción para mostrar: ")

    elements = []
    if display_choice == '2':
        while True:
            print("1. Hotel")
            print("2. Avión")
            print("3. Coche")
            print("4. Terminar selección")
            sub_choice = input("Selecciona una opción: ")
            if sub_choice == '1' and "Hotel" not in elements:
                elements.append("Hotel")
            elif sub_choice == '2' and "Avión" not in elements:
                elements.append("Avión")
            elif sub_choice == '3' and "Coche" not in elements:
                elements.append("Coche")
            elif sub_choice == '4':
                break
            else:
                print("Opción inválida o ya seleccionada, intenta de nuevo.")
        print(f"Mostrando reservas con: {', '.join(elements)}")

    print("\n--- Filtrar Reservas ---")
    filters = []
    while True:
        print("1. Por fechas")
        print("2. Por DNI")
        print("3. Por ID de reserva")
        print("4. Por disponibilidad de vuelo, hotel o coche")
        print("5. Por lugar")
        print("6. Terminar selección de filtros")
        filter_choice = input("Selecciona una opción: ")
        if filter_choice == '1' and "Fechas" not in filters:
            filters.append("Fechas")
        elif filter_choice == '2' and "DNI" not in filters:
            filters.append("DNI")
        elif filter_choice == '3' and "ID de reserva" not in filters:
            filters.append("ID de reserva")
        elif filter_choice == '4' and "Disponibilidad de vuelo, hotel o coche" not in filters:
            filters.append("Disponibilidad de vuelo, hotel o coche")
        elif filter_choice == '5' and "Lugar" not in filters:
            filters.append("Lugar")
        elif filter_choice == '6':
            break
        else:
            print("Opción inválida o ya seleccionada, intenta de nuevo.")
    print(f"Aplicando filtros: {', '.join(filters)}")

    # Generar consulta SQL según selección
    query = "SELECT * FROM RESERVAS"
    joins = []
    where_clauses = []

    if "Hotel" in elements:
        joins.append("LEFT JOIN RESERVAS_HOTEL ON RESERVAS.ID_RESERVA = RESERVAS_HOTEL.ID_RESERVA")
    if "Avión" in elements:
        joins.append("LEFT JOIN RESERVAS_AVION ON RESERVAS.ID_RESERVA = RESERVAS_AVION.ID_RESERVA")
    if "Coche" in elements:
        joins.append("LEFT JOIN RESERVAS_COCHE ON RESERVAS.ID_RESERVA = RESERVAS_COCHE.ID_RESERVA")

    if "Fechas" in filters:
        start_date = input("Introduce la fecha de inicio (YYYY-MM-DD): ")
        end_date = input("Introduce la fecha de fin (YYYY-MM-DD): ")
        where_clauses.append(f"RESERVAS.FECHA_INICIO >= '{start_date}' AND RESERVAS.FECHA_FINAL <= '{end_date}'")
    if "DNI" in filters:
        dni = input("Introduce el DNI del cliente: ")
        where_clauses.append(f"RESERVAS.DNI = '{dni}'")
    if "ID de reserva" in filters:
        id_reserva = input("Introduce el ID de la reserva: ")
        where_clauses.append(f"RESERVAS.ID_RESERVA = '{id_reserva}'")
    if "Disponibilidad de vuelo, hotel o coche" in filters:
        availability = input("Introduce el tipo (Vuelo, Hotel, Coche): ").lower()
        if availability == "vuelo":
            where_clauses.append("RESERVAS_AVION.ID_RESERVA IS NOT NULL")
        elif availability == "hotel":
            where_clauses.append("RESERVAS_HOTEL.ID_RESERVA IS NOT NULL")
        elif availability == "coche":
            where_clauses.append("RESERVAS_COCHE.ID_RESERVA IS NOT NULL")
    if "Lugar" in filters:
        lugar = input("Introduce el lugar: ")
        where_clauses.append(f"(RESERVAS_HOTEL.ID_HOTEL IN (SELECT ID_HOTEL FROM HOTELES WHERE CIUDAD = '{lugar}') OR RESERVAS_COCHE.MATRICULA_COCHE IN (SELECT MATRICULA_COCHE FROM COCHES WHERE AEROPUERTO = '{lugar}'))")

    if joins:
        query += " " + " ".join(joins)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    print(f"Ejecutando consulta: {query}")
    connection = connect_to_database()
    if connection:
        results, column_names = execute_query(connection, query)
        if results is not None:
            display_results(results, column_names)
        connection.close()

def update_data():
    print("\n--- Actualizar ---")
    print("Opciones para actualizar datos de tiers, precios de hoteles y aviónes.")

    # Implementar actualizaciones de tiers y precios

def delete_data():
    print("\n--- Eliminar ---")
    print("Opciones para eliminar reservas, vuelos y clientes sin actividad.")

    # Implementar eliminación de datos

def search_statistics():
    print("\n--- Buscar Estadísticas ---")
    print("Opciones para mostrar y filtrar estadísticas.")

    # Implementar búsqueda de estadísticas

def main():
    print("Bienvenido al sistema de gestión de base de datos.")
    connection = connect_to_database()

    if connection:
        while True:
            show_menu()
            choice = input("\nSelecciona una opción del menú: ")

            if choice == '1':
                list_reservations()
            elif choice == '2':
                update_data()
            elif choice == '3':
                delete_data()
            elif choice == '4':
                search_statistics()
            elif choice == '5':
                print("\nGracias por usar el sistema. Adiós.")
                break
            else:
                print("\nOpción inválida. Por favor, intenta de nuevo.")

        if connection.is_connected():
            connection.close()
            print("Conexión cerrada correctamente.")

if __name__ == "__main__":
    main()
