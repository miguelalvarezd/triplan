import mysql.connector
from mysql.connector import Error
import pandas as pd
import random
from datetime import datetime

import matplotlib.pyplot as plt
import folium
import webbrowser
import os

class ResumenVuelos:
            def __init__(self, id_reserva, id_vuelo, origen, destino, hora_salida, precio_base, precio_extra, id_vuelo_vuelta, origen_vuelta, destino_vuelta, hora_salida_vuelta, precio_base_vuelta, precio_extra_vuelta):
                self.id_reserva = id_reserva
                self.id_vuelo = id_vuelo
                self.origen = origen
                self.destino = destino
                self.hora_salida = hora_salida
                self.precio_base = precio_base
                self.precio_extra = precio_extra

                self.id_vuelo_vuelta = id_vuelo_vuelta
                self.origen_vuelta = origen_vuelta
                self.destino_vuelta = destino_vuelta
                self.hora_salida_vuelta = hora_salida_vuelta
                self.precio_base_vuelta = precio_base_vuelta
                self.precio_extra_vuelta = precio_extra_vuelta

try:
    # Establecer la conexión
    conexion = mysql.connector.connect(
        host="localhost",       # Cambia por tu dirección de servidor MySQL
        user="root",            # Tu usuario de MySQL
        password="password",      # Contraseña de tu usuario
        database="db_triplan"   # Nombre de la base de datos a conectar
    )

    if conexion.is_connected():
        print("\nConectando a la base de datos...")
        print("===========================================")
        print("Conexión exitosa a la base de datos.")
        cursor = conexion.cursor()


    def listar_vuelos(conexion):
        """Lista los vuelos registrados, permite filtrar por número, ID o vuelos del próximo mes."""
        try:
            cursor = conexion.cursor()

            # Preguntar cómo listar los vuelos
            print("\nSeleccione una opción para listar vuelos:")
            print("[1] Listar un número específico de vuelos")
            print("[2] Ver un vuelo específico por ID")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                num_vuelos = int(input("¿Cuántos vuelos desea ver? "))
                consulta = f"SELECT ID_VUELO, ID_TRAYECTO, MATRICULA_AVION, FECHA_VUELO FROM VUELOS LIMIT {num_vuelos}"
                cursor.execute(consulta)
                vuelos = cursor.fetchall()
                print("\nVuelos registrados:")
                print("-------------------------------------------")
                print("ID Vuelo | ID Trayecto | Matrícula | Fecha")
                print("-------------------------------------------")
                for vuelo in vuelos:
                    print(f"{vuelo[0]:<9} | {vuelo[1]:<11} | {vuelo[2]:<10} | {vuelo[3]}")
                print("-------------------------------------------")

            elif opcion == "2":
                vuelo_id = input("Ingrese el ID del vuelo que desea ver: ").strip()
                consulta = "SELECT ID_VUELO, ID_TRAYECTO, MATRICULA_AVION, FECHA_VUELO FROM VUELOS WHERE ID_VUELO = %s"
                cursor.execute(consulta, (vuelo_id,))
                vuelo = cursor.fetchone()
                if vuelo:
                    print("\nVuelo encontrado:")
                    print("-------------------------------------------")
                    print("ID Vuelo | ID Trayecto | Matrícula | Fecha")
                    print(f"{vuelo[0]:<9} | {vuelo[1]:<11} | {vuelo[2]:<10} | {vuelo[3]}")
                    print("-------------------------------------------")
                else:
                    print("Vuelo no encontrado.")

            else:
                print("Opción inválida.")

        except Exception as e:
            print(f"Error al listar vuelos: {e}")


    def listar_coches(conexion):
        """Lista los coches disponibles para alquiler o permite buscar por ID."""
        try:
            cursor = conexion.cursor()
            
            print("\nSeleccione una opción para listar coches:")
            print("[1] Listar un número específico de coches")
            print("[2] Ver un coche específico por ID (matrícula)")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                num_coches = int(input("¿Cuántos coches desea ver? "))
                consulta = f"SELECT MATRICULA_COCHE, MODELO_COCHE, PRECIO_POR_DIA, AEROPUERTO FROM COCHES LIMIT {num_coches}"
                cursor.execute(consulta)
                coches = cursor.fetchall()

                print("\nCoches disponibles:")
                print("-------------------------------------------")
                print("Matrícula Coche | Modelo      | Precio por Día | Aeropuerto")
                print("-------------------------------------------")
                for coche in coches:
                    print(f"{coche[0]:<15} | {coche[1]:<12} | {coche[2]:<15} | {coche[3]}")
                print("-------------------------------------------")
            
            elif opcion == "2":
                matricula = input("Ingrese la matrícula del coche que desea ver: ").strip()
                consulta = "SELECT MATRICULA_COCHE, MODELO_COCHE, PRECIO_POR_DIA, AEROPUERTO FROM COCHES WHERE MATRICULA_COCHE = %s"
                cursor.execute(consulta, (matricula,))
                coche = cursor.fetchone()
                if coche:
                    print("\nCoche encontrado:")
                    print("-------------------------------------------")
                    print("Matrícula Coche | Modelo      | Precio por Día | Aeropuerto")
                    print(f"{coche[0]:<15} | {coche[1]:<12} | {coche[2]:<15} | {coche[3]}")
                    print("-------------------------------------------")
                else:
                    print("Coche no encontrado.")
            
            else:
                print("Opción inválida.")
        
        except Exception as e:
            print(f"Error al listar coches: {e}")

    def listar_hoteles(conexion):
        """Lista los hoteles disponibles o permite buscar por ID."""
        try:
            cursor = conexion.cursor()

            print("\nSeleccione una opción para listar hoteles:")
            print("[1] Listar un número específico de hoteles")
            print("[2] Ver un hotel específico por ID")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                num_hoteles = int(input("¿Cuántos hoteles desea ver? "))
                consulta = f"SELECT ID_HOTEL, NOMBRE_HOTEL, CIUDAD, PRECIO_POR_NOCHE FROM HOTELES LIMIT {num_hoteles}"
                cursor.execute(consulta)
                hoteles = cursor.fetchall()

                print("\nHoteles disponibles:")
                print("-------------------------------------------")
                print("ID Hotel | Nombre Hotel     | Ciudad   | Precio por Noche")
                print("-------------------------------------------")
                for hotel in hoteles:
                    print(f"{hotel[0]:<8} | {hotel[1]:<15} | {hotel[2]:<8} | {hotel[3]}")
                print("-------------------------------------------")
            
            elif opcion == "2":
                id_hotel = input("Ingrese el ID del hotel que desea ver (ej. H-0097): ").strip()
                consulta = "SELECT ID_HOTEL, NOMBRE_HOTEL, CIUDAD, PRECIO_POR_NOCHE FROM HOTELES WHERE ID_HOTEL = %s"
                cursor.execute(consulta, (id_hotel,))
                hotel = cursor.fetchone()
                if hotel:
                    print("\nHotel encontrado:")
                    print("-------------------------------------------")
                    print("ID Hotel | Nombre Hotel     | Ciudad   | Precio por Noche")
                    print(f"{hotel[0]:<8} | {hotel[1]:<15} | {hotel[2]:<8} | {hotel[3]}")
                    print("-------------------------------------------")
                else:
                    print("Hotel no encontrado.")
            
            else:
                print("Opción inválida.")
        
        except Exception as e:
            print(f"Error al listar hoteles: {e}")

    def listar_reservas(conexion):
        """Lista las reservas realizadas o permite buscar por ID."""
        try:
            cursor = conexion.cursor()

            print("\nSeleccione una opción para listar reservas:")
            print("[1] Listar un número específico de reservas")
            print("[2] Ver una reserva específica por ID")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                num_reservas = int(input("¿Cuántas reservas desea ver? "))
                consulta = f"SELECT ID_RESERVA, DNI, FECHA_INICIO, FECHA_FINAL FROM RESERVAS LIMIT {num_reservas}"
                cursor.execute(consulta)
                reservas = cursor.fetchall()

                print("\nReservas realizadas:")
                print("-------------------------------------------")
                print("ID Reserva | DNI       | Fecha Inicio | Fecha Final")
                print("-------------------------------------------")
                for reserva in reservas:
                    print(f"{reserva[0]:<10} | {reserva[1]:<9} | {reserva[2]:<12} | {reserva[3]}")
                print("-------------------------------------------")
            
            elif opcion == "2":
                id_reserva = input("Ingrese el ID de la reserva que desea ver (ej. R-00041): ").strip()
                consulta = "SELECT ID_RESERVA, DNI, FECHA_INICIO, FECHA_FINAL FROM RESERVAS WHERE ID_RESERVA = %s"
                cursor.execute(consulta, (id_reserva,))
                reserva = cursor.fetchone()
                if reserva:
                    print("\nReserva encontrada:")
                    print("-------------------------------------------")
                    print("ID Reserva | DNI       | Fecha Inicio | Fecha Final")
                    print(f"{reserva[0]:<10} | {reserva[1]:<9} | {reserva[2]:<12} | {reserva[3]}")
                    print("-------------------------------------------")
                else:
                    print("Reserva no encontrada.")
            
            else:
                print("Opción inválida.")
        
        except Exception as e:
            print(f"Error al listar reservas: {e}")


    def actualizar_hotel(conexion):
        """Actualiza información de un hotel."""
        try:
            cursor = conexion.cursor()

            # Solicitar detalles del hotel
            id_hotel = input("Ingrese el ID del hotel a actualizar: ").strip().upper()
            nuevo_precio = float(input("Ingrese el nuevo precio por noche: "))

            # Actualizar en la base de datos
            consulta = "UPDATE HOTELES SET PRECIO_POR_NOCHE = %s WHERE ID_HOTEL = %s"
            valores = (nuevo_precio, id_hotel)
            cursor.execute(consulta, valores)
            conexion.commit()

            if cursor.rowcount > 0:
                print("Hotel actualizado correctamente.")
            else:
                print("No se encontró el hotel con el ID proporcionado.")
        except Exception as e:
            print(f"Error al actualizar hotel: {e}")

    def eliminar_reserva(conexion):
        """Elimina una reserva específica."""
        try:
            cursor = conexion.cursor()

            # Solicitar ID de reserva
            id_reserva = input("Ingrese el ID de la reserva a eliminar: ").strip().upper()

            # Eliminar de la base de datos
            consulta = "DELETE FROM RESERVAS WHERE ID_RESERVA = %s"
            cursor.execute(consulta, (id_reserva,))
            conexion.commit()

            if cursor.rowcount > 0:
                print("Reserva eliminada correctamente.")
            else:
                print("No se encontró una reserva con el ID proporcionado.")
        except Exception as e:
            print(f"Error al eliminar reserva: {e}")

    def menu_empleados(conexion):
        """Menú principal para empleados."""
        while True:
            print("\n" + "=" * 40)
            print("            MENÚ DE EMPLEADOS            ")
            print("=" * 40)
            print("[1] Listar vuelos")
            print("[2] Listar coches")
            print("[3] Listar hoteles")
            print("[4] Listar reservas")
            print("[5] Actualizar precio de hotel")
            print("[6] Eliminar reserva")
            print("[7] Mostrar gráficas")
            print("[8] Salir")
            print("=" * 40)

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                listar_vuelos(conexion)
            elif opcion == "2":
                listar_coches(conexion)  # Función para listar coches
            elif opcion == "3":
                listar_hoteles(conexion)  # Función para listar hoteles
            elif opcion == "4":
                listar_reservas(conexion)  # Función para listar reservas
            elif opcion == "5":
                actualizar_hotel(conexion)  # Función para actualizar precio de hotel
            elif opcion == "6":
                eliminar_reserva(conexion)  # Función para eliminar una reserva
            elif opcion == "7":
                mostrar_graficos(conexion)  # Función para eliminar una reserva
            elif opcion == "8":
                print("Cerrando sesión de empleado...")
                break
            else:
                print("Opción inválida. Por favor, intente de nuevo.")

    def fetch_data(query):
        with conexion.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return pd.DataFrame(result)


    def mostrar_graficos(conexion):
        """Función para mostrar el gráfico seleccionado."""
        while True:
            print("\n" + "=" * 40)
            print("           MENÚ DE GRÁFICOS DISPONIBLES            ")
            print("=" * 40)
            print("[1] Número de vuelos por modelo de avión")
            print("[2] Ingresos totales por trayecto")
            print("[3] Número de reservas por nivel de cliente (TIER)")
            print("[4] Cantidad de reservas por ciudad de origen")
            print("[5] Precio promedio por noche en hoteles por ciudad")
            print("[6] Cantidad de coches disponibles por aeropuerto")
            print("[7] Mapa de los vuelos")
            print("[8] Volver al menú principal")
            print("=" * 40)

            opcion = input("Seleccione un gráfico para mostrar: ").strip()

            if opcion == "1":
                mostrar_numero_vuelos_por_modelo(conexion)
            elif opcion == "2":
                mostrar_ingresos_por_trayecto(conexion)
            elif opcion == "3":
                mostrar_reservas_por_tier(conexion)
            elif opcion == "4":
                mostrar_reservas_por_origen(conexion)
            elif opcion == "5":
                mostrar_precio_promedio_hoteles(conexion)
            elif opcion == "6":
                mostrar_coches_por_aeropuerto(conexion)
            elif opcion == "7":
                plot_map_aeropuertos()
            elif opcion == "8":
                print("Volviendo al menú principal...")
                break
            else:
                print("Opción inválida. Por favor, intente de nuevo.")


    # 1. Número de vuelos por modelo de avión
    def mostrar_numero_vuelos_por_modelo(conexion):
        """Gráfico de Número de vuelos por modelo de avión."""
        query_vuelos_por_modelo = """
            SELECT 
                MODELOS_AVION.MODELO_AVION, 
                COUNT(VUELOS.ID_VUELO) AS NUMERO_DE_VUELOS
            FROM 
                MODELOS_AVION
            LEFT JOIN 
                AVIONES ON MODELOS_AVION.MODELO_AVION = AVIONES.MODELO_AVION
            LEFT JOIN 
                VUELOS ON AVIONES.MATRICULA_AVION = VUELOS.MATRICULA_AVION
            GROUP BY 
                MODELOS_AVION.MODELO_AVION
            ORDER BY 
                NUMERO_DE_VUELOS DESC;
        """
        df_vuelos_por_modelo = fetch_data(query_vuelos_por_modelo)
        df_vuelos_por_modelo.columns = ["MODELO_AVION", "NUMERO_DE_VUELOS"]  # Rename columns

        # Gráfica 1
        plt.figure(figsize=(8, 5))
        plt.bar(
            df_vuelos_por_modelo["MODELO_AVION"],
            df_vuelos_por_modelo["NUMERO_DE_VUELOS"],
            color="skyblue",
        )
        plt.title("Número de Vuelos por Modelo de Avión")
        plt.xlabel("Modelo de Avión")
        plt.ylabel("Número de Vuelos")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # 2. Ingresos totales por trayecto
    def mostrar_ingresos_por_trayecto(conexion):
        """Gráfico de Ingresos totales por trayecto."""
        query_ingresos_por_trayecto = """
            SELECT 
                TRAYECTOS.ID_TRAYECTO,
                TRAYECTOS.ORIGEN,
                TRAYECTOS.DESTINO,
                SUM(TRAYECTOS.PRECIO_TRAYECTO + COALESCE(ASIENTOS.PRECIO_EXTRA, 0)) AS INGRESOS_TOTALES
            FROM 
                TRAYECTOS
            JOIN 
                VUELOS ON TRAYECTOS.ID_TRAYECTO = VUELOS.ID_TRAYECTO
            JOIN 
                RESERVAS_AVION ON VUELOS.ID_VUELO = RESERVAS_AVION.ID_VUELO
            JOIN 
                ASIENTOS ON RESERVAS_AVION.NUMERO_ASIENTO = ASIENTOS.NUMERO_ASIENTO
            GROUP BY 
                TRAYECTOS.ID_TRAYECTO, TRAYECTOS.ORIGEN, TRAYECTOS.DESTINO
            ORDER BY 
                INGRESOS_TOTALES DESC
            LIMIT 10;
        """
        df_ingresos_por_trayecto = fetch_data(query_ingresos_por_trayecto)
        df_ingresos_por_trayecto.columns = ["ID_TRAYECTO", "ORIGEN", "DESTINO", "INGRESOS_TOTALES"]

        # Gráfica 2
        plt.figure(figsize=(8, 5))
        plt.barh(
            df_ingresos_por_trayecto["ID_TRAYECTO"],
            df_ingresos_por_trayecto["INGRESOS_TOTALES"],
            color="green",
        )
        plt.title("Ingresos Totales por Trayecto")
        plt.xlabel("Ingresos Totales")
        plt.ylabel("Trayecto")
        plt.tight_layout()
        plt.show()

    # 3. Número de reservas por nivel de cliente (TIER)
    def mostrar_reservas_por_tier(conexion):
        """Gráfico de Número de reservas por nivel de cliente (TIER)."""
        query_reservas_por_tier = """
            SELECT 
                CLIENTES.TIER, 
                COUNT(RESERVAS.ID_RESERVA) AS NUMERO_DE_RESERVAS
            FROM 
                CLIENTES
            LEFT JOIN 
                RESERVAS ON CLIENTES.DNI = RESERVAS.DNI
            GROUP BY 
                CLIENTES.TIER
            ORDER BY 
                NUMERO_DE_RESERVAS DESC;
        """
        df_reservas_por_tier = fetch_data(query_reservas_por_tier)
        df_reservas_por_tier.columns = ["TIER", "NUMERO_DE_RESERVAS"]

        # Gráfica 3
        plt.figure(figsize=(8, 5))
        plt.pie(
            df_reservas_por_tier["NUMERO_DE_RESERVAS"],
            labels=df_reservas_por_tier["TIER"],
            autopct="%1.1f%%",
            startangle=140,
            colors=["brown", "silver", "blue", "gold"],
        )
        plt.title("Distribución de Reservas por Nivel de Cliente (TIER)")
        plt.tight_layout()
        plt.show()

    # 4. Cantidad de reservas por ciudad de origen
    def mostrar_reservas_por_origen(conexion):
        """Gráfico de Cantidad de reservas por ciudad de origen."""
        query_reservas_por_origen = """
            SELECT 
                TRAYECTOS.ORIGEN, 
                COUNT(RESERVAS_AVION.ID_RESERVA) AS NUMERO_DE_RESERVAS
            FROM 
                TRAYECTOS
            JOIN 
                VUELOS ON TRAYECTOS.ID_TRAYECTO = VUELOS.ID_TRAYECTO
            JOIN 
                RESERVAS_AVION ON VUELOS.ID_VUELO = RESERVAS_AVION.ID_VUELO
            GROUP BY 
                TRAYECTOS.ORIGEN
            ORDER BY 
                NUMERO_DE_RESERVAS DESC
            LIMIT 10;
        """
        df_reservas_por_origen = fetch_data(query_reservas_por_origen)
        df_reservas_por_origen.columns = ["ORIGEN", "NUMERO_DE_RESERVAS"]

        # Gráfica 4
        plt.figure(figsize=(8, 5))
        plt.bar(
            df_reservas_por_origen["ORIGEN"],
            df_reservas_por_origen["NUMERO_DE_RESERVAS"],
            color="orange",
        )
        plt.title("Cantidad de Reservas por Ciudad de Origen")
        plt.xlabel("Ciudad de Origen")
        plt.ylabel("Número de Reservas")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # 5. Precio promedio por noche en hoteles por ciudad
    def mostrar_precio_promedio_hoteles(conexion):
        """Gráfico de Precio promedio por noche en hoteles por ciudad."""
        query_precio_promedio_por_ciudad = """
            SELECT 
                HOTELES.CIUDAD, 
                AVG(HOTELES.PRECIO_POR_NOCHE) AS PRECIO_PROMEDIO
            FROM 
                HOTELES
            GROUP BY 
                HOTELES.CIUDAD
            ORDER BY 
                PRECIO_PROMEDIO DESC;
        """
        df_precio_promedio_por_ciudad = fetch_data(query_precio_promedio_por_ciudad)
        df_precio_promedio_por_ciudad.columns = ["CIUDAD", "PRECIO_PROMEDIO"]

        # Gráfica 5
        plt.figure(figsize=(8, 5))
        plt.bar(
            df_precio_promedio_por_ciudad["CIUDAD"],
            df_precio_promedio_por_ciudad["PRECIO_PROMEDIO"],
            color="purple",
        )
        plt.title("Precio Promedio por Noche en Hoteles por Ciudad")
        plt.xlabel("Ciudad")
        plt.ylabel("Precio Promedio")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # 6. Cantidad de coches disponibles por aeropuerto
    def mostrar_coches_por_aeropuerto(conexion):
        """Gráfico de Cantidad de coches disponibles por aeropuerto."""
        query_coches_por_aeropuerto = """
            SELECT 
                COCHES.AEROPUERTO, 
                COUNT(COCHES.MATRICULA_COCHE) AS NUMERO_DE_COCHES
            FROM 
                COCHES
            GROUP BY 
                COCHES.AEROPUERTO
            ORDER BY 
                NUMERO_DE_COCHES DESC;
        """
        df_coches_por_aeropuerto = fetch_data(query_coches_por_aeropuerto)
        df_coches_por_aeropuerto.columns = ["AEROPUERTO", "NUMERO_DE_COCHES"]

        # Gráfica 6
        plt.figure(figsize=(8, 5))
        plt.pie(
            df_coches_por_aeropuerto["NUMERO_DE_COCHES"],
            labels=df_coches_por_aeropuerto["AEROPUERTO"],
            autopct=lambda pct: f"{int(round(pct * sum(df_coches_por_aeropuerto['NUMERO_DE_COCHES']) / 100))}",
            startangle=140,
        )
        plt.title("Cantidad de Coches Disponibles por Aeropuerto")
        plt.tight_layout()
        plt.show()



    # Función para ejecutar consultas
    def execute_query(query, data=None):
        try:
            with conexion.cursor() as cursor:
                if data:
                    cursor.executemany(query, data)
                else:
                    cursor.execute(query)
            conexion.commit()
            print("Consulta ejecutada correctamente.")
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")

    # Comprobar si existe la tabla AEROPUERTOS, si no existe, crearla
    def check_create_aeropuertos():
        create_table_query = """
        CREATE TABLE IF NOT EXISTS AEROPUERTOS (
            CODIGO VARCHAR(10) PRIMARY KEY,
            NOMBRE VARCHAR(100),
            LATITUD DECIMAL(10, 6),
            LONGITUD DECIMAL(10, 6)
        );
        """
        execute_query(create_table_query)


    # Función para mostrar el mapa de aeropuertos
    def plot_map_aeropuertos():
        try:

            check_create_aeropuertos()
            # Consultar datos de aeropuertos
            query_aeropuertos = """
                SELECT CODIGO, NOMBRE, LATITUD, LONGITUD FROM AEROPUERTOS
            """

            df_aeropuertos = fetch_data(query_aeropuertos)
            if isinstance(df_aeropuertos.columns[0], int):  # Si la primera columna es un índice numérico
                df_aeropuertos.columns = ['CODIGO', 'NOMBRE', 'LATITUD', 'LONGITUD']

            # Crear mapa centrado en una ubicación general (por ejemplo, el centro de EE.UU.)
            folium_map = folium.Map(location=[39.8283, -98.5795], zoom_start=5)

            # Agregar marcadores para cada aeropuerto
            airport_locations = []
            for _, aeropuerto in df_aeropuertos.iterrows():
                location = [aeropuerto['LATITUD'], aeropuerto['LONGITUD']]
                airport_locations.append(location)
                
                # Agregar marcador para cada aeropuerto
                folium.Marker(
                    location=location,
                    popup=f"{aeropuerto['NOMBRE']} ({aeropuerto['CODIGO']})",
                    icon=folium.Icon(color="blue"),  # Íconos azules para todos
                ).add_to(folium_map)
            
            # Añadir líneas entre todos los aeropuertos (conectar cada aeropuerto con todos los demás)
            for i in range(len(airport_locations)):
                for j in range(i + 1, len(airport_locations)):
                    folium.PolyLine(
                        locations=[airport_locations[i], airport_locations[j]],
                        color="blue",  # Líneas azules
                        weight=2.5,
                        opacity=0.8,
                    ).add_to(folium_map)

            # Ruta para guardar el archivo HTML
            output_map_dir = "output"
            os.makedirs(output_map_dir, exist_ok=True)
            map_output = os.path.join(output_map_dir, "aeropuertos_map.html")
            
            # Guardar el mapa como archivo HTML
            folium_map.save(map_output)
            print(f"Mapa de aeropuertos guardado en {map_output}")
            
            # Abrir el mapa en el navegador
            webbrowser.open(f"file://{os.path.abspath(map_output)}")
        
        except Exception as e:
            print(f"Error al generar el mapa de aeropuertos: {e}")

    def RellenarAeropuertos():
        #LEEMOS CSV Y LO GUARDAMOS EN ESTE DICCIONARIO COMO: CODIGO, CIUDAD
        df = pd.read_csv("aeropuertos.csv", delimiter=";",encoding="utf-8")  
        aeropuertos = dict(zip(df['Codigo'].astype(str), df['Ciudad']))

        return aeropuertos

    def BuscarTrayecto(origen, destino):
        consulta = "SELECT HORA_SALIDA, PRECIO_TRAYECTO, ID_TRAYECTO FROM TRAYECTOS WHERE ORIGEN = %s AND DESTINO = %s"
        cursor.execute(consulta, (origen, destino))
        return cursor.fetchall()

    def BuscarVuelosCompatibles(origen, destino, fecha_vuelo):
        consulta = "SELECT T.ID_TRAYECTO, T.PRECIO_TRAYECTO, T.HORA_SALIDA, V.ID_VUELO, V.FECHA_VUELO FROM TRAYECTOS AS T, VUELOS AS V WHERE T.ID_TRAYECTO = V.ID_TRAYECTO AND T.ORIGEN = %s AND T.DESTINO =  %s AND  V.FECHA_VUELO = %s"
        cursor.execute(consulta, (origen, destino, fecha_vuelo))
        return cursor.fetchall()

    def ReservarBillete(reserva):
        aeropuertos = RellenarAeropuertos()
              
        #BUCLE ELECCION ORIGEN - DESTINO
        while True:
            #seleccion de origen-destino
            print("\n¡Iniciamos una reserva de vuelo!")
            print("===========================================")
            print("\nLista de aeropuertos disponibles:")
            print("-------------------------------------------")

            
            for codigo in aeropuertos.keys():
                print(f'{codigo}:   {aeropuertos[codigo]}')

            reserva['origen'] = input('\nIntroduzca el código (AAA) de la ciudad de origen: ').upper()
            reserva['destino'] = input('Introduzca el código (AAA) de la ciudad de destino: ').upper()

            #BUSCAMOS VUELOS COMPATIBLES CON ORGIEN DESTINO Y FECHA INICIAL
            vuelos = BuscarVuelosCompatibles(reserva['origen'], reserva['destino'], reserva['fecha_inicio'])

            if vuelos:
                break
            else:
                print(f"\nNo hay vuelos compatibles desde {reserva['origen']} hasta {reserva['destino']} el día {reserva['fecha_inicio']}.")
                print("-------------------------------------------")
                dec = input('Desea probar de nuevo con otro origen/destino? (S/N)')
                if(dec) == 'N':
                    return

        # IMPRIMIMOS LOS VUELOS DISPONIBLES Y LE PEDIMOS AL USUARIO QUE ESCOJA UNO
        v_sel = {}  # Diccionario donde se guardarán los vuelos seleccionados
        print("\nVuelos disponibles:")
        print("-------------------------------------------")

        # Enumeramos los vuelos disponibles y los mostramos
        for index, v in enumerate(vuelos, start=1):
            print(f"{index}- Hora: {v[2]} | Código: {v[3]} | Precio: {v[1]}€")
            v_sel[index] = v  # Guardamos el vuelo seleccionado en el diccionario

        print("-------------------------------------------")

        # Pedimos al usuario que elija el vuelo
        try:
            sel = int(input('\nElija el número correspondiente al vuelo que desee reservar: '))

            # Comprobamos si la opción seleccionada es válida
            if sel not in v_sel:
                raise ValueError("Selección inválida. Por favor, elija un número válido.")
            
            # Guardamos los datos del vuelo seleccionado
            reserva['hora_vuelo'] = v_sel[sel][2]
            reserva['precio_base'] = v_sel[sel][1]
            reserva['id_trayecto'] = v_sel[sel][0]
            reserva['id_vuelo'] = v_sel[sel][3]

            # Mostramos los datos del vuelo seleccionado de forma bonita
            print(f"\nHa elegido el vuelo con la hora: {reserva['hora_vuelo']}")
            print(f"Precio base: {reserva['precio_base']}€")
            print("-------------------------------------------")

        except ValueError as e:
            print(e)  # Mostramos el mensaje de error si la entrada no es válida
            # Puedes agregar un bucle para volver a pedir la selección si es necesario

        #ELEGIR LA CLASE DE ASIENTO
        consulta = "SELECT DISTINCT CLASE_BILLETE FROM ASIENTOS WHERE NUMERO_ASIENTO NOT IN (SELECT NUMERO_ASIENTO FROM RESERVAS_AVION WHERE ID_VUELO = %s)"
        cursor.execute(consulta, (reserva['id_vuelo'], ))
        clases_posibles = cursor.fetchall()

        if clases_posibles:
            c_sel = {}
            index = 1

            for c in clases_posibles:
                print(f'{index}- {c[0]}')
                c_sel[index] = c
                index += 1
            sel = int(input('\nElija el número correspondiente a la clase que prefiera: '))


        else:
            print("\nNo quedan asientos en este vuelo, disculpe.")
            print("===========================================")
            return
        
        reserva['clase'] = c_sel[sel][0]
        print(reserva['clase'])

        #ASIGNACION ASIENTO
        #asientos posibles para ese vuelo (teoricos menos reservados)
        consulta = "SELECT NUMERO_ASIENTO, PRECIO_EXTRA FROM ASIENTOS WHERE CLASE_BILLETE = %s AND NUMERO_ASIENTO NOT IN (SELECT NUMERO_ASIENTO FROM RESERVAS_AVION WHERE ID_VUELO = %s)"
        cursor.execute(consulta, (reserva['clase'],reserva['id_vuelo']))
        asientos_posibles = cursor.fetchall()

        #SELECCIONAMOS UN ASIENTO AL AZAR DE LOS ASIENTOS POSIBLES
        asiento = asientos_posibles[random.randint(0, len(asientos_posibles))]
        reserva['num_asiento'] = asiento[0]
        reserva['precio_extra'] = asiento[1]
        print(f'Asiento: {reserva['num_asiento']} Precio extra: {reserva['precio_extra']}')

        reserva['clase'] = reserva['clase']
        reserva['precio'] = reserva['precio_base'] + reserva['precio_extra']


        # Preguntar por VUELO DE VUELTA -----------------------
        vuelo_vuelta = input("\n¿Desea reservar un vuelo de vuelta? (S/N):").upper()
        print("===========================================")
        
        if vuelo_vuelta == 'S':
            # Invertir origen y destino para el vuelo de vuelta
            reserva['origen_vuelta'] = reserva['destino']
            reserva['destino_vuelta'] = reserva['origen']

            vuelos_vuelta = BuscarVuelosCompatibles(reserva['origen_vuelta'], reserva['destino_vuelta'], reserva['fecha_final'])

            if vuelos_vuelta:
                v_sel = {}  # Diccionario donde se guardarán los vuelos de vuelta seleccionados
                print("\nVuelos de vuelta disponibles:")
                print("-------------------------------------------")
                
                # Enumeramos los vuelos de vuelta y los mostramos
                for index, v in enumerate(vuelos_vuelta, start=1):
                    print(f"{index}- Hora: {v[2]} | Código: {v[3]} | Precio: {v[1]}€")
                    v_sel[index] = v  # Guardamos el vuelo seleccionado en el diccionario
                
                print("-------------------------------------------")

                # Pedimos al usuario que elija el vuelo de vuelta
                try:
                    sel = int(input('\nElija el número correspondiente al vuelo de vuelta que desee reservar: '))
                    
                    # Comprobamos si la opción seleccionada es válida
                    if sel not in v_sel:
                        raise ValueError("Selección inválida. Por favor, elija un número válido.")
                    
                    # Guardamos los datos del vuelo de vuelta seleccionado
                    reserva['hora_vuelo_vuelta'] = v_sel[sel][2]
                    reserva['precio_base_vuelta'] = v_sel[sel][1]
                    reserva['id_trayecto_vuelta'] = v_sel[sel][0]
                    reserva['id_vuelo_vuelta'] = v_sel[sel][3]
                    
                    # Mostramos el vuelo seleccionado con un mensaje bonito
                    print(f"\nHa elegido el vuelo de vuelta con la hora: {reserva['hora_vuelo_vuelta']}")
                    print(f"Precio base: {reserva['precio_base_vuelta']}€")
                    print("-------------------------------------------")

                except ValueError as e:
                    print(e)  # Mostramos el mensaje de error si la entrada no es válida
                    # Puedes agregar un bucle para volver a pedir la selección si es necesario

                #ASIGNACION ASIENTO (ASUMIMOS MISMA CLASE QUE IDA)
                #asientos posibles para ese vuelo (teoricos menos reservados)
                consulta = "SELECT NUMERO_ASIENTO, PRECIO_EXTRA FROM ASIENTOS WHERE CLASE_BILLETE = %s AND NUMERO_ASIENTO NOT IN (SELECT NUMERO_ASIENTO FROM RESERVAS_AVION WHERE ID_VUELO = %s)"
                cursor.execute(consulta, (reserva['clase'],reserva['id_vuelo_vuelta']))
                asientos_posibles = cursor.fetchall()

                #SELECCIONAMOS UN ASIENTO AL AZAR DE LOS ASIENTOS POSIBLES
                asiento = asientos_posibles[random.randint(0, len(asientos_posibles))]
                reserva['num_asiento_vuelta'] = asiento[0]
                reserva['precio_extra_vuelta'] = asiento[1]
                print(f'Asiento: {reserva['num_asiento_vuelta']} Precio extra: {reserva['precio_extra_vuelta']}')

                reserva['precio_vuelta'] = reserva['precio_base_vuelta'] + reserva['precio_extra_vuelta']
            
            else:
                print('Perdone pero no quedan vuelos de vuelta con esta combinacion')

        if 'precio_vuelta' not in reserva:
            reserva['precio_vuelta'] = 0

        reserva['precio_total'] = reserva['precio'] + reserva['precio_vuelta']
        print('Reserva final')
        for key in reserva.keys():
            print(f'{key}:  {reserva[key]}')


        # Insertar la reserva DE IDA en la base de datos
        consulta = "INSERT INTO RESERVAS_AVION (ID_VUELO, ID_RESERVA, NUMERO_BILLETE, NUMERO_ASIENTO) VALUES (%s, %s, %s, %s)"
        valores = (reserva['id_vuelo'], reserva['id_reserva'], GenerarIDBillete(reserva['id_trayecto']), reserva['num_asiento'])
        cursor.execute(consulta, valores)
        conexion.commit()

        #INSERTAMOS VUELO VUELTA EN DB
        if 'id_vuelo_vuelta' in reserva:  # Solo si se ha reservado vuelo de vuelta
            consulta = "INSERT INTO RESERVAS_AVION (ID_VUELO, ID_RESERVA, NUMERO_BILLETE, NUMERO_ASIENTO) VALUES (%s, %s, %s, %s)"
            valores = (reserva['id_vuelo_vuelta'], reserva['id_reserva'], GenerarIDBillete(reserva['id_trayecto_vuelta']), reserva['num_asiento_vuelta'])
            cursor.execute(consulta, valores)
            conexion.commit()
        
        print("\nReserva de vuelos finalizada y almacenada en la base de datos.")

    def ReservarHotel(reserva):
        
        print("\nVamos a reservar una habitación de hotel.")
        print("===========================================")

        if 'destino' not in reserva:
            reserva['destino'] = input('¿En qué ciudad desea reservar el hotel?')

        #BUSCAMOS LOS HOTELES DISPONIBLES PARA EL DESTINO
        consulta = "SELECT NOMBRE_HOTEL, PRECIO_POR_NOCHE, ID_HOTEL, DIRECCION FROM HOTELES WHERE CIUDAD = %s" 
        cursor.execute(consulta, (reserva['destino'],))
        hoteles = cursor.fetchall()

        if hoteles:
            h_sel = {}
            index = 1

            print("\nHoteles disponibles en el destino:")
            print("-------------------------------------------")        
            for h in hoteles:
                print(f'{index}- {h[0]} ({h[3]}):  {h[1]}€')
                h_sel[index] = h
                index += 1

            #PEDIMOS AL USUARIO ELEGIR UNO DE LOS HOTELES
            sel = int(input('\nElija el número correspondiente al hotel que desee reservar: '))
            reserva['hotel'] = h_sel[sel][0]
            reserva['direccion_hotel'] = h_sel[sel][3]
            reserva['precio_base_hotel'] = h_sel[sel][1]
            reserva['id_hotel'] = h_sel[sel][2]
            print(f'Ha elegido el hotel {reserva['hotel']} / {reserva['id_hotel']} ')

            #MOSTRAMOS LOS TIPOS DE HABITACION DISPONIBLES PARA ESE HOTEL
            consulta = "SELECT TIPO_HABITACION, NUMERO_HABITACION, PRECIO_EXTRA FROM HABITACIONES WHERE ID_HOTEL = %s AND NUMERO_HABITACION NOT IN (SELECT NUMERO_HABITACION FROM RESERVAS_HOTEL WHERE ID_HOTEL = %s AND ID_RESERVA IN (SELECT ID_RESERVA FROM RESERVAS WHERE FECHA_INICIO <= %s AND FECHA_FINAL >= %s));" 
            cursor.execute(consulta, (reserva['id_hotel'],reserva['id_hotel'], reserva['fecha_inicio'], reserva['fecha_final']))
            habitaciones_disp = cursor.fetchall()


            if habitaciones_disp:
                h_sel = {}
                index = 1
                print('Tipo habitacion disponibles:')
                for h in habitaciones_disp:
                    print(f'{index}- {h[0]} // {h[1]} // Precio extra: {h[2]}€')
                    h_sel[index] = h
                    index += 1

                #PEDIMOS AL CLIENTE ELEGIR LA HABITACION QUE DESEE
                sel = int(input('\nElija el número correspondiente a la habitacion que desea reservar: '))

                reserva['numero_habitacion'] = h_sel[sel][1]
                reserva['tipo_habitacion'] = h_sel[sel][0]
                reserva['precio_extra_hotel'] = h_sel[sel][2]
                reserva['precio_total_hotel'] = reserva['precio_base_hotel'] + reserva['precio_extra_hotel']

                print(f"\nHabitación reservada en {reserva['hotel']}. Total: {reserva['precio_total_hotel']}€.")
                print("===========================================")


                #INSERTAR RESERVA EN BASE DE DATOS
                consulta = "INSERT INTO RESERVAS_HOTEL (ID_RESERVA, ID_HOTEL, NUMERO_HABITACION) VALUES (%s, %s, %s)"
                valores = (reserva['id_reserva'], reserva['id_hotel'], reserva['numero_habitacion'])
                cursor.execute(consulta, valores)
                conexion.commit()

                print("Reserva de alojamiento finalizada y almacenada en la base de datos.")
                
            else:
                print('No hay habitaciones disponibles para las fechas señaladas')
                return
        else:
            print('No hay hoteles disponibles para las fechas señaladas')
           
    def ReservarCoche(reserva):
        print("\nVamos a reservar un coche.")
        print("===========================================")


        #SI NO SE HA RESERVADO UN VUELO ANTES DEBEMOS PREGUNTAR POR EL LUAGR DONDE SE ALQUILA EL COCHE
        if 'destino' not in reserva:
            reserva['destino'] = input('¿En qué ciudad desea reservar el coche?')

        #consulta = "SELECT MODELO_COCHE, PRECIO_POR_DIA, MATRICULA_COCHE FROM COCHES WHERE AEROPUERTO = %s" 
        consulta = "SELECT MODELO_COCHE, PRECIO_POR_DIA, MATRICULA_COCHE FROM COCHES WHERE AEROPUERTO = %s AND MATRICULA_COCHE NOT IN (SELECT MATRICULA_COCHE FROM RESERVAS_COCHE WHERE AEROPUERTO = %s AND ID_RESERVA IN (SELECT ID_RESERVA FROM RESERVAS WHERE FECHA_INICIO <= %s AND FECHA_FINAL >= %s));"
        cursor.execute(consulta, (reserva['destino'],reserva['destino'], reserva['fecha_inicio'], reserva['fecha_final']))
        coches = cursor.fetchall()

        if coches:
            c_sel = {}  # Diccionario para almacenar los coches disponibles
            index = 1
            print("\nCoches disponibles:")
            print("-------------------------------------------")

            # Rellenamos el diccionario y mostramos los coches
            for index, c in enumerate(coches, start=1):
                print(f"{index}- Modelo: {c[0]} | Precio por día: {c[1]}€")
                c_sel[index] = c  # Asociamos el índice con los datos del coche
            
            print("-------------------------------------------")

            try:
                # Pedimos al cliente que elija un coche
                sel = int(input('\nElija el número correspondiente al coche que desea reservar: '))

                # Validamos si la selección es válida
                if sel not in c_sel:
                    raise ValueError("Selección inválida. Por favor, elija un número válido.")
                
                # Guardamos los datos del coche seleccionado en la reserva
                reserva['matricula_coche'] = c_sel[sel][2]
                reserva['modelo_coche'] = c_sel[sel][0]
                reserva['precio_coche_x_dia'] = c_sel[sel][1]

                # CALCULAMOS LOS DÍAS QUE VA A DURAR LA RESERVA
                dias_dif = DiferenciaFechas(reserva['fecha_inicio'], reserva['fecha_final'])

                # Calculamos el precio total del coche
                reserva['precio_total_coche'] = reserva['precio_coche_x_dia'] * dias_dif
                print(f"\nCoche reservado: {reserva['modelo_coche']} con matrícula {reserva['matricula_coche']}.")
                print(f"Total: {reserva['precio_total_coche']}€ por {dias_dif} días.")
                print("===========================================")

                # ACTUALIZAMOS LA BASE DE DATOS
                consulta = "INSERT INTO RESERVAS_COCHE (ID_RESERVA, MATRICULA_COCHE) VALUES (%s, %s)"
                valores = (reserva['id_reserva'], reserva['matricula_coche'])
                cursor.execute(consulta, valores)
                conexion.commit()

                print("Reserva de coche finalizada y almacenada en la base de datos.")
            
            except ValueError as e:
                # Manejamos errores de entrada inválida
                print(f"Error: {e}")
                # Puedes agregar un bucle para permitir al cliente intentar de nuevo si es necesario
        else:
            print('Perdone, pero no hay coches disponibles.')


    def RegistrarCliente():
        cliente = {}
        cliente['dni'] = input('\nIntroduzca su DNI: ').upper()
        cliente['nombre'] = input('Introduzca su nombre: ')
        cliente['telefono'] = int(input('Introduzca su teléfono (9 digitos sin separación): '))
        cliente['tier'] = 'BRONZE'

        consulta = "INSERT INTO clientes (dni, nombre, telefono, tier) VALUES (%s, %s, %s, %s)"
        valores = (cliente['dni'], cliente['nombre'], cliente['telefono'], cliente['tier'])
        cursor.execute(consulta, valores)
        conexion.commit()
        print('Cliente registrado exitosamente.')
        return cliente

    def GenerarIDReserva():
        cursor.execute("SELECT ID_RESERVA FROM RESERVAS")
        reservas_existentes = cursor.fetchall()
        numero = random.randint(0, 99999)

        # Formatearlo con 5 dígitos, incluyendo ceros a la izquierda si es necesario
        numero_formateado = f"{numero:05d}" 
        id_reserva = 'R-'+ str(numero_formateado)

        while(id_reserva in reservas_existentes):
            id_reserva = 'R-'+ str(numero_formateado)

        print(id_reserva)

        return id_reserva
    
    def GenerarIDBillete(id_trayecto):

        cursor.execute("SELECT NUMERO_BILLETE FROM RESERVAS_AVION")
        billetes_existentes = cursor.fetchall()
        numero = random.randint(0, 9999)

        numero_formateado = f"{numero:04d}" 
        id_billete = id_trayecto +'-'+ str(numero_formateado)

        while(id_billete in billetes_existentes):
            id_billete = 'R-'+ str(numero_formateado)

        print(id_billete)

        return id_billete
    
    def DiferenciaFechas(fecha_in, fecha_fin):
        formato = "%Y-%m-%d"  # Formato de las fechas
        fecha_in = datetime.strptime(fecha_in, formato)
        fecha_fin = datetime.strptime(fecha_fin, formato)

        diferencia = fecha_in - fecha_fin
        dias = abs(diferencia.days)
        print(f'Dias: {dias}')
        return dias

    def EliminarReserva(cliente):
        #IMPRIMIR RESERVAS
        #MOSTRAMOS LAS RESERVAS HECHAS POR EL USUARIO
        consulta = "SELECT * FROM RESERVAS WHERE DNI= %s"
        cursor.execute(consulta, (cliente['dni'],))
        reservas = cursor.fetchall()
        cursor.nextset()

        print("\nSUS RESERVAS SON:")
        print("===========================================")
        index = 1
        if reservas:
            # print(reservas)
            for r in reservas:
                print(f'{index} {r[0]}')
                index += 1

            cancelacion = (input('Introduzca el código de su reserva: '))
            consulta = "DELETE FROM RESERVAS WHERE ID_RESERVA = %s"
            cursor.execute(consulta, (cancelacion,))
            conexion.commit()
            print('Reserva eliminada correctamente!')

        else:
            print('No tiene reservas todavía\n')

    def VisualizarReservas(cliente):
        #MOSTRAMOS LAS RESERVAS HECHAS POR EL USUARIO
        consulta = "SELECT * FROM RESERVAS WHERE DNI= %s"
        cursor.execute(consulta, (cliente['dni'],))
        reservas = cursor.fetchall()

        

        print('SUS RESERVAS SON:')
        print("===========================================")
        index = 1
        if reservas:
            # print(reservas)
            print("-------------------------------------------")
            for r in reservas:
                print(f'{index}- {r[0]}:')
                index += 1

                #billetes asociados a esa reserva
                consulta = "SELECT ID_VUELO, NUMERO_ASIENTO FROM RESERVAS_AVION WHERE ID_RESERVA= %s"
                cursor.execute(consulta, (r[0],))
                billetes = cursor.fetchall()

                #Si la reserva tiene billetes los imprimimos
                if billetes:
                    print('     BILLETES: ')
                    print('         Número vuelo  ||  Número asiento: ')

                    for b in billetes:
                        print(f'         {b[0]}          ||   {b[1]}')
                    
                    print('')
                

                #HABITACIONES ASOCIADAS A LA RESERVA
                consulta = "SELECT NOMBRE_HOTEL, CIUDAD FROM HOTELES WHERE ID_HOTEL IN(SELECT ID_HOTEL FROM RESERVAS_HOTEL WHERE ID_RESERVA = %s)"
                cursor.execute(consulta, (r[0],))
                habitaciones = cursor.fetchall()
                if habitaciones:
                    print('     HABITACIONES: ')
                    print('         Nombre hotel        ||  Ciudad ')

                    for h in habitaciones:
                        print(f'         {h[0]}          ||   {h[1]}')
                    print('')

                #COCHES ASOCIADOS A LA RESERVA
                consulta = "SELECT MATRICULA_COCHE, MODELO_COCHE, AEROPUERTO FROM COCHES WHERE MATRICULA_COCHE IN(SELECT MATRICULA_COCHE FROM RESERVAS_COCHE WHERE ID_RESERVA = %s)"
                cursor.execute(consulta, (r[0],))
                coches = cursor.fetchall()
                if coches:
                    print('     COCHES: ')
                    print('         Coche                   ||  Ciudad ')

                    for c in coches:
                        print(f'         {c[1]}({c[0]})          ||   {c[2]}')
                    print('')

        else:
            print('No tiene reservas todavía\n')

    def GenerarRecibo(reserva, cliente):
        # Verificamos que las claves necesarias existan en 'reserva'
        if 'id_vuelo' in reserva and 'id_vuelo_vuelta' in reserva:
            vuelos_info = ResumenVuelos(
                reserva['id_reserva'],
                reserva.get('id_vuelo', None),
                reserva.get('origen', None),
                reserva.get('destino', None),
                reserva.get('hora_salida', None),
                reserva.get('precio_base', 0),
                reserva.get('precio_extra', 0),
                reserva.get('id_vuelo_vuelta', None),
                reserva.get('origen_vuelta', None),
                reserva.get('destino_vuelta', None),
                reserva.get('hora_salida_vuelta', None),
                reserva.get('precio_base_vuelta', 0),
                reserva.get('precio_extra_vuelta', 0)
            )

        elif 'id_vuelo' in reserva and 'id_vuelo_vuelta' not in reserva:
            vuelos_info = ResumenVuelos(
                reserva['id_reserva'],
                reserva['id_vuelo'],
                reserva['origen'],
                reserva['destino'],
                reserva.get('hora_salida', None),
                reserva['precio_base'],
                reserva['precio_extra'],
                None, None, None, None, None, None
            )
        elif 'id_vuelo' not in reserva and 'id_vuelo_vuelta' in reserva:
            vuelos_info = ResumenVuelos(
                reserva['id_reserva'],
                None, None, None, None, None, None,
                reserva['id_vuelo_vuelta'],
                reserva['origen_vuelta'],
                reserva['destino_vuelta'],
                reserva.get('hora_salida_vuelta', None),
                reserva['precio_base_vuelta'],
                reserva['precio_extra_vuelta']
            )
        else:
            vuelos_info = ResumenVuelos(
                reserva['id_reserva'], None, None, None, None, None, None,
                None, None, None, None, None, None
            )

        precio_tot = 0
        dias_dif = DiferenciaFechas(reserva['fecha_inicio'], reserva['fecha_final'])

        cursor.execute("SELECT DESCUENTO FROM TIERS WHERE TIER = %s", (cliente['tier'],))
        descuento = cursor.fetchone()

        nombre_informe = vuelos_info.id_reserva + '.txt'
        with open(nombre_informe, "w") as archivo:
            archivo.write(f"Este es el recibo de la reserva {vuelos_info.id_reserva}\n")
            archivo.write('--------------------------------------------\n')

            # Información de vuelos
            if 'id_vuelo' in reserva:
                archivo.write('\nINFROMACION VUELO IDA\n')
                archivo.write(f'Id vuelo: {vuelos_info.id_vuelo}\n')
                archivo.write(f'Itinerario: {vuelos_info.origen} ({vuelos_info.hora_salida} // {reserva["fecha_inicio"]}) ---> {vuelos_info.destino}\n')
                archivo.write(f'Precio: {vuelos_info.precio_base}(BASE) + {vuelos_info.precio_extra}(EXTRA) = {vuelos_info.precio_extra + vuelos_info.precio_base}EUR\n')
                precio_tot += reserva['precio_base']

            if 'id_vuelo_vuelta' in reserva:
                archivo.write('\n\nINFROMACION VUELO VUELTA\n')
                archivo.write(f'Id vuelo: {vuelos_info.id_vuelo_vuelta}\n')
                archivo.write(f'Itinerario: {vuelos_info.origen_vuelta} ({vuelos_info.hora_salida_vuelta} // {reserva["fecha_final"]}) ---> {vuelos_info.destino_vuelta}\n')
                archivo.write(f'Precio: {vuelos_info.precio_base_vuelta}(BASE) + {vuelos_info.precio_extra_vuelta}(EXTRA) = {vuelos_info.precio_extra_vuelta + vuelos_info.precio_base_vuelta}EUR\n')
                precio_tot += reserva['precio_base_vuelta']

            # Información de habitación
            if 'numero_habitacion' in reserva:
                archivo.write('\n\nINFROMACION HABITACIÓN\n')
                archivo.write(f'Id hotel: {reserva["id_hotel"]}\n')
                archivo.write(f'Hotel: {reserva["hotel"]}  //  Direccion: {reserva["direccion_hotel"]}  //  Ciudad: {reserva["destino"]}\n')
                archivo.write(f'Numero habitacion: {reserva["numero_habitacion"]} ({reserva["tipo_habitacion"]})\n')
                archivo.write(f'Precio: {reserva["precio_base_hotel"]}(BASE) + {reserva["precio_extra_hotel"]}(EXTRA) = {reserva["precio_total_hotel"]}EUR\n')
                precio_tot += reserva['precio_total_hotel']

            # Información de coche
            if 'matricula_coche' in reserva:
                archivo.write('\n\nINFROMACION COCHE\n')
                archivo.write(f'Matricula: {reserva["matricula_coche"]}\n')
                archivo.write(f'Modelo coche: {reserva["modelo_coche"]}  //  Aeropuerto de recogida: {reserva["destino"]}\n')
                archivo.write(f'Precio: {reserva["precio_coche_x_dia"]}(Precio x dia) * {dias_dif}(días alquiler) = {reserva["precio_total_coche"]}EUR\n')
                precio_tot += reserva['precio_total_coche']

            archivo.write('\n\n---------------------------------------------')
            archivo.write(f'\nPRECIO TOTAL RESERVA = {precio_tot}')
            archivo.write(f'\nDESCUENTO POR TIER = {descuento[0] * 100}%')
            archivo.write(f'\nPRECIO FINAL = {(1 - descuento[0]) * precio_tot}')

        
    def main():

        #Preguntamos por el rol del usuario
        print("\n¡Bienvenido a Triplan!")
        print("===========================================")
        print("¿Usted es cliente o empleado?:")
        print("1- Cliente")
        print("2- Empleado")


        rol = int(input('Seleccione un número: '))

        if rol == 1: # cliente
            cliente = {}

            if input('\n¿Es la primera vez que usa nuestra plataforma? (S/N): ').upper() == 'S':
                #damos de alta al nuevo cliente
                cliente = RegistrarCliente()

            else:
                #pedimos que se identifique como cliente existente
                cliente['dni'] = input('Introduzca su DNI: ').upper()
                cursor.execute("SELECT nombre, telefono, tier FROM clientes WHERE dni = %s", (cliente['dni'],))
                datos_cliente = cursor.fetchone()

                if datos_cliente:
                    cliente['nombre'] = datos_cliente[0]
                    cliente['telefono'] = datos_cliente[1]
                    cliente['tier'] = datos_cliente[2]

                else:
                    print("\n===========================================")
                    print("Cliente no encontrado. Por favor, regístrese.")
                    print("===========================================")
                    print("Cliente registrado exitosamente.")

                    cliente = RegistrarCliente()

            print(f"\nBienvenido, {cliente['nombre']}!")
            print("===========================================")

            #pregunto si quiere hacer reserva o cancelar
            while True:
                print("¿Qué quiere hacer?")
                print("1. Realizar una reserva nueva")
                print("2. Cancelar una reserva existente")
                print("3. Ver mis reservas")
                print("4. Salir de Triplan")
                accion = int(input('\nIntroduzca la opción que desea realizar:'))

                #PROCEDEMOS EMPEZAR LA RESERVA
                if accion == 1:
                    reserva = {}
                    #reserva['fecha_inicio'] = '2024-09-12'
                    #reserva['fecha_final'] = '2024-09-30'
                    
                    reserva['id_reserva'] = GenerarIDReserva()

                    print('En qué fechas requiere nuestros servicios?')
                    reserva['fecha_inicio'] = input('Fecha de inicio (YYYY-MM-DD):')
                    reserva['fecha_final']= input('Fecha de fin (YYYY-MM-DD):')

                    #CREAMOS LA RESERVA EN LA BASE DE DATOS
                    consulta = "INSERT INTO RESERVAS (ID_RESERVA, DNI, FECHA_INICIO, FECHA_FINAL) VALUES (%s, %s, %s, %s)"
                    valores = (reserva['id_reserva'], cliente['dni'], reserva['fecha_inicio'], reserva['fecha_final'])
                    cursor.execute(consulta, valores)
                    conexion.commit()

                    #EMPEZAMOS CON LAS RESERVAS ESPECIFICAS
                    while True:
                        tipo_reserva = int(input('¿Qué tipo de reserva desea realizar?\n1- Avión\n2- Hotel\n3- Coche\nEscoja una opción:'))

                        if tipo_reserva == 1:
                            ReservarBillete(reserva)
                            if(input('Quiere añadir una reserva de hotel? (S/N)') == 'S'):
                                ReservarHotel(reserva)

                            if(input('Quiere añadir una reserva de coche? (S/N)') == 'S'):
                                ReservarCoche(reserva)
                            break 

                        elif tipo_reserva == 2:
                            ReservarHotel(reserva)
                            break

                        elif tipo_reserva == 3:
                            ReservarCoche(reserva)
                            break

                    #UNA VEZ FINALIZA LA RESERVA SE PROCEDE A GENERAR UN RECIBO DE LA MISMA CON LOS DATOS ESENCIALES
                    print("\nSe va a generar un archivo .txt con el recibo de su reserva.")
                    print("===========================================")
 
                    GenerarRecibo(reserva, cliente)
                    
                #ELIMINAMOS LA RESERVA
                elif accion == 2:
                    EliminarReserva(cliente)

                #VISUALIZAR RESERVA
                elif accion == 3:  
                    VisualizarReservas(cliente)
                
                #SALIR DEL PROGRAMA
                elif accion == 4: 
                    #LOG OUT
                    print(f"\n¡Gracias por usar Triplan, {cliente['nombre']}!")
                    print("===========================================")

                    break
            

        elif rol == 2: # empleado
            #empleados --> verificación con contraseña
            password = input('\nIntroduzca la contraseña para empleados:')

            while(password != 'elefantes'):
                password = input('Contraseña incorrecta, por favor inténtelo de nuevo:')

            print("\nContraseña correcta.")
            print("===========================================")

            menu_empleados(conexion)

            # añadir todo lo de empleados
            

    if __name__ == '__main__':
        main()

except Error as e:
    print(f"Error al conectar a la base de datos: {e}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
        print("\n===========================================")
        print("Conexión cerrada correctamente.")

