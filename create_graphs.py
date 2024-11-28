from getpass import getpass

import matplotlib.pyplot as plt
import pandas as pd
import pymysql

# Solicitar la contraseña de forma interactiva
db_password = getpass("Introduce la contraseña para la base de datos MySQL: ")

# Conexión a la base de datos MySQL
connection = pymysql.connect(
    host="localhost",
    user="root",
    password=db_password,
    database="DB_TRIPLAN",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


# Función para ejecutar consultas y devolver resultados como DataFrame
def fetch_data(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    return pd.DataFrame(result)


# 1. Número de vuelos por modelo de avión
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

# Gráfica
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

# Gráfica
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

# Gráfica
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


# Cierre de conexión
connection.close()
