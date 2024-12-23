SELECT 
    TRAYECTOS.ID_TRAYECTO,
    TRAYECTOS.ORIGEN,
    TRAYECTOS.DESTINO,
    COUNT(RESERVAS_AVION.NUMERO_BILLETE) AS TOTAL_BILLETES_VENDIDOS,
    SUM(TRAYECTOS.PRECIO_TRAYECTO + ASIENTOS.PRECIO_EXTRA) AS INGRESOS_TOTALES
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
HAVING 
    INGRESOS_TOTALES > 1000;


SELECT 
    CLIENTES.TIER,
    CLIENTES.DNI,
    CLIENTES.NOMBRE,
    COUNT(RESERVAS.ID_RESERVA) AS NUMERO_DE_RESERVAS
FROM 
    CLIENTES
JOIN 
    RESERVAS ON CLIENTES.DNI = RESERVAS.DNI
WHERE 
    RESERVAS.FECHA_INICIO >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY 
    CLIENTES.DNI, CLIENTES.TIER, CLIENTES.NOMBRE
HAVING 
    NUMERO_DE_RESERVAS > 3
ORDER BY 
    NUMERO_DE_RESERVAS DESC;


SELECT 
    HOTELES.CIUDAD,
    HOTELES.NOMBRE_HOTEL,
    AVG(COUNT_RESERVAS.TOTAL_OCUPACION) AS OCUPACION_PROMEDIO
FROM 
    HOTELES
JOIN (
    SELECT 
        RESERVAS_HOTEL.ID_HOTEL, 
        COUNT(RESERVAS_HOTEL.ID_RESERVA) AS TOTAL_OCUPACION
    FROM 
        RESERVAS_HOTEL
    GROUP BY 
        RESERVAS_HOTEL.ID_HOTEL
) AS COUNT_RESERVAS ON HOTELES.ID_HOTEL = COUNT_RESERVAS.ID_HOTEL
GROUP BY 
    HOTELES.CIUDAD, HOTELES.NOMBRE_HOTEL
ORDER BY 
    OCUPACION_PROMEDIO DESC;


SELECT 
    CLIENTES.NOMBRE,
    CLIENTES.TELEFONO,
    COCHES.AEROPUERTO,
    COUNT(RESERVAS_COCHE.ID_RESERVA) AS TOTAL_RESERVAS
FROM 
    CLIENTES
JOIN 
    RESERVAS ON CLIENTES.DNI = RESERVAS.DNI
JOIN 
    RESERVAS_COCHE ON RESERVAS.ID_RESERVA = RESERVAS_COCHE.ID_RESERVA
JOIN 
    COCHES ON RESERVAS_COCHE.MATRICULA_COCHE = COCHES.MATRICULA_COCHE
WHERE 
    COCHES.AEROPUERTO = (
        SELECT 
            AEROPUERTO
        FROM 
            COCHES
        GROUP BY 
            AEROPUERTO
        ORDER BY 
            COUNT(AEROPUERTO) DESC
        LIMIT 1
    )
GROUP BY 
    CLIENTES.NOMBRE, CLIENTES.TELEFONO, COCHES.AEROPUERTO;


SELECT 
    MODELOS_AVION.FABRICANTE,
    MODELOS_AVION.MODELO_AVION,
    COALESCE(AVG(INGRESOS.INGRESOS_TOTALES), 0) AS PROMEDIO_INGRESOS
FROM 
    MODELOS_AVION
LEFT JOIN 
    AVIONES ON MODELOS_AVION.MODELO_AVION = AVIONES.MODELO_AVION
LEFT JOIN 
    VUELOS ON AVIONES.MATRICULA_AVION = VUELOS.MATRICULA_AVION
LEFT JOIN (
    SELECT 
        RESERVAS_AVION.ID_VUELO,
        SUM(COALESCE(TRAYECTOS.PRECIO_TRAYECTO, 0) + COALESCE(ASIENTOS.PRECIO_EXTRA, 0)) AS INGRESOS_TOTALES
    FROM 
        RESERVAS_AVION
    LEFT JOIN 
        TRAYECTOS ON RESERVAS_AVION.ID_VUELO = TRAYECTOS.ID_TRAYECTO
    LEFT JOIN 
        ASIENTOS ON RESERVAS_AVION.NUMERO_ASIENTO = ASIENTOS.NUMERO_ASIENTO
    GROUP BY 
        RESERVAS_AVION.ID_VUELO
) AS INGRESOS ON VUELOS.ID_VUELO = INGRESOS.ID_VUELO
GROUP BY 
    MODELOS_AVION.FABRICANTE, MODELOS_AVION.MODELO_AVION
HAVING 
    PROMEDIO_INGRESOS >= 0;





DELETE FROM VUELOS
WHERE ID_VUELO NOT IN (
    SELECT DISTINCT ID_VUELO
    FROM RESERVAS_AVION
    JOIN RESERVAS ON RESERVAS_AVION.ID_RESERVA = RESERVAS.ID_RESERVA
    WHERE FECHA_INICIO >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
);


UPDATE TRAYECTOS
SET PRECIO_TRAYECTO = PRECIO_TRAYECTO * 1.10
WHERE MODELO_AVION IN (
    SELECT MODELO_AVION
    FROM MODELOS_AVION
    WHERE FABRICANTE = 'BOEING'
);

DELETE FROM CLIENTES
WHERE DNI NOT IN (
    SELECT DISTINCT DNI
    FROM RESERVAS
    WHERE FECHA_FINAL >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
);

UPDATE HABITACIONES
SET PRECIO_EXTRA = PRECIO_EXTRA + 20
WHERE ID_HOTEL IN (
    SELECT ID_HOTEL
    FROM (
        SELECT 
            H.ID_HOTEL,
            COUNT(R.ID_RESERVA) AS TOTAL_RESERVAS
        FROM 
            HABITACIONES H
        LEFT JOIN 
            RESERVAS_HOTEL R ON H.ID_HOTEL = R.ID_HOTEL
        GROUP BY 
            H.ID_HOTEL
    ) AS RESERVAS
    WHERE TOTAL_RESERVAS > 2
);


UPDATE CLIENTES
SET TIER = 
    CASE 
        WHEN TIER = 'PLATINUM' THEN 'GOLD'
        WHEN TIER = 'GOLD' THEN 'SILVER'
        WHEN TIER = 'SILVER' THEN 'BRONZE'
        ELSE 'BRONZE'
    END
WHERE DNI NOT IN (
    SELECT DISTINCT DNI
    FROM RESERVAS
    WHERE FECHA_FINAL >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
);


