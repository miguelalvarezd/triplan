import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend

import matplotlib.pyplot as plt
import pandas as pd
import io

def fetch_data(query, conexion):
        with conexion.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return pd.DataFrame(result)

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
    df_vuelos_por_modelo = fetch_data(query_vuelos_por_modelo, conexion)
    df_vuelos_por_modelo.columns = ["MODELO_AVION", "NUMERO_DE_VUELOS"]  # Rename columns

    # Gráfica 1
    plt.figure(figsize=(8, 5))
    plt.bar(
        df_vuelos_por_modelo["MODELO_AVION"],
        df_vuelos_por_modelo["NUMERO_DE_VUELOS"],
        color="skyblue",
    )
    plt.title("Number of Flights per Airplane Model")
    plt.xlabel("Airplane Model")
    plt.ylabel("Number of Flights")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return buffer

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
    df_ingresos_por_trayecto = fetch_data(query_ingresos_por_trayecto, conexion)
    df_ingresos_por_trayecto.columns = ["ID_TRAYECTO", "ORIGEN", "DESTINO", "INGRESOS_TOTALES"]

    # Gráfica 2
    plt.figure(figsize=(8, 5))
    plt.barh(
        df_ingresos_por_trayecto["ID_TRAYECTO"],
        df_ingresos_por_trayecto["INGRESOS_TOTALES"],
        color="green",
    )
    plt.title("Total Revenues per Route (€)")
    plt.xlabel("Total Revenues (€)")
    plt.ylabel("Route")
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return buffer

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
    df_reservas_por_tier = fetch_data(query_reservas_por_tier, conexion)
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
    plt.title("Distribution of Reservations per Client Tier")
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return buffer

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
    df_reservas_por_origen = fetch_data(query_reservas_por_origen, conexion)
    df_reservas_por_origen.columns = ["ORIGEN", "NUMERO_DE_RESERVAS"]

    # Gráfica 4
    plt.figure(figsize=(8, 5))
    plt.bar(
        df_reservas_por_origen["ORIGEN"],
        df_reservas_por_origen["NUMERO_DE_RESERVAS"],
        color="orange",
    )
    plt.title("Number of Reservations per City of Origin")
    plt.xlabel("Origin City")
    plt.ylabel("Number of Reservations")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return buffer

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
    df_precio_promedio_por_ciudad = fetch_data(query_precio_promedio_por_ciudad, conexion)
    df_precio_promedio_por_ciudad.columns = ["CIUDAD", "PRECIO_PROMEDIO"]

    # Gráfica 5
    plt.figure(figsize=(8, 5))
    plt.bar(
        df_precio_promedio_por_ciudad["CIUDAD"],
        df_precio_promedio_por_ciudad["PRECIO_PROMEDIO"],
        color="purple",
    )
    plt.title("Average Nightly Price in Hotels per City (€/night)")
    plt.xlabel("City")
    plt.ylabel("Average Price (€/night)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return buffer

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
    df_coches_por_aeropuerto = fetch_data(query_coches_por_aeropuerto, conexion)
    df_coches_por_aeropuerto.columns = ["AEROPUERTO", "NUMERO_DE_COCHES"]

    # Gráfica 6
    plt.figure(figsize=(8, 5))
    plt.pie(
        df_coches_por_aeropuerto["NUMERO_DE_COCHES"],
        labels=df_coches_por_aeropuerto["AEROPUERTO"],
        autopct=lambda pct: f"{int(round(pct * sum(df_coches_por_aeropuerto['NUMERO_DE_COCHES']) / 100))}",
        startangle=140,
    )
    plt.title("Number of Cars Available per Airport")
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()  

    return buffer