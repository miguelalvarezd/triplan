DROP DATABASE IF EXISTS DB_TRIPLAN;
CREATE DATABASE DB_TRIPLAN;

USE DB_TRIPLAN;

DROP TABLE IF EXISTS AVIONES;
DROP TABLE IF EXISTS MODELOS_AVION;
DROP TABLE IF EXISTS ASIENTOS;
DROP TABLE IF EXISTS TRAYECTOS;
DROP TABLE IF EXISTS RESERVAS;
DROP TABLE IF EXISTS RESERVAS_HOTEL;
DROP TABLE IF EXISTS RESERVAS_COCHE;
DROP TABLE IF EXISTS RESERVAS_AVION;
DROP TABLE IF EXISTS VUELOS;
DROP TABLE IF EXISTS CLIENTES;
DROP TABLE IF EXISTS TIERS;
DROP TABLE IF EXISTS HOTEL;
DROP TABLE IF EXISTS COCHES;
DROP TABLE IF EXISTS HABITACIONES;
DROP TABLE IF EXISTS MODELOS_COCHE;

CREATE TABLE MODELOS_AVION (
  MODELO_AVION CHAR(3) NOT NULL,
  FABRICANTE VARCHAR(10) NOT NULL,
  RANGO_KM INT,
  CONSTRAINT PK2 PRIMARY KEY (MODELO_AVION),
  CONSTRAINT CHK_MODELO_AVION_LENGTH CHECK (CHAR_LENGTH(MODELO_AVION) = 3)
);

CREATE TABLE AVIONES (
  MODELO_AVION VARCHAR(3) NOT NULL,
  MATRICULA_AVION CHAR(5) NOT NULL,
  FECHA_COMPRA DATE,
  FECHA_ULTIMA_REVISION DATE,
  CONSTRAINT PK1 PRIMARY KEY (MATRICULA_AVION),
  CONSTRAINT FK1 FOREIGN KEY (MODELO_AVION) REFERENCES MODELOS_AVION (MODELO_AVION) ON DELETE CASCADE,
  CONSTRAINT CHK_MATRICULA_AVION_LENGTH CHECK (CHAR_LENGTH(MATRICULA_AVION) = 5)
);

CREATE TABLE ASIENTOS (
  NUMERO_ASIENTO VARCHAR(3) NOT NULL,
  CLASE_BILLETE VARCHAR(15) NOT NULL,
  PRECIO_EXTRA INT,
  CONSTRAINT PK3 PRIMARY KEY (NUMERO_ASIENTO)
);

CREATE TABLE TRAYECTOS (
  ID_TRAYECTO VARCHAR(7) NOT NULL,
  ORIGEN CHAR(3) NOT NULL,
  DESTINO CHAR(3) NOT NULL,
  HORA_SALIDA TIME NOT NULL,
  HORA_LLEGADA TIME NOT NULL,
  PRECIO_TRAYECTO INT NOT NULL,
  MODELO_AVION VARCHAR(3) NOT NULL,
  CONSTRAINT PK4 PRIMARY KEY (ID_TRAYECTO),
  CONSTRAINT CHK_ORIGEN_LENGTH CHECK (CHAR_LENGTH(ORIGEN) = 3),
  CONSTRAINT CHK_DESTINO_LENGTH CHECK (CHAR_LENGTH(DESTINO) = 3)
);

CREATE TABLE TIERS (
  TIER VARCHAR(15) NOT NULL,
  DESCUENTO DECIMAL(3,2) NOT NULL,
  CONSTRAINT PK11 PRIMARY KEY (TIER)
);

CREATE TABLE CLIENTES (
  DNI CHAR(9) NOT NULL,
  NOMBRE VARCHAR(30) NOT NULL,
  TELEFONO BIGINT,
  TIER VARCHAR(15) NOT NULL,
  CONSTRAINT PK10 PRIMARY KEY (DNI),
  CONSTRAINT FK14 FOREIGN KEY (TIER) REFERENCES TIERS (TIER) ON DELETE CASCADE,
  CONSTRAINT CHK_DNI_LENGTH CHECK (CHAR_LENGTH(DNI) = 9)
);

CREATE TABLE RESERVAS (
  ID_RESERVA CHAR(7) NOT NULL,
  DNI CHAR(9) NOT NULL,
  FECHA_INICIO DATE NOT NULL,
  FECHA_FINAL DATE,
  CONSTRAINT PK5 PRIMARY KEY (ID_RESERVA),
  CONSTRAINT FK2 FOREIGN KEY (DNI) REFERENCES CLIENTES (DNI) ON DELETE CASCADE,
  CONSTRAINT CHK_ID_RESERVA_LENGTH CHECK (CHAR_LENGTH(ID_RESERVA) = 7)
);

CREATE TABLE HOTELES (
  ID_HOTEL CHAR(6) NOT NULL,
  NOMBRE_HOTEL VARCHAR(30) NOT NULL,
  CIUDAD VARCHAR(20) NOT NULL,
  DIRECCION VARCHAR(50) NOT NULL,
  HABITACIONES_TOTALES INT NOT NULL,
  PRECIO_POR_NOCHE INT NOT NULL,
  CONSTRAINT PK12 PRIMARY KEY (ID_HOTEL),
  CONSTRAINT CHK_ID_HOTEL_LENGTH CHECK (CHAR_LENGTH(ID_HOTEL) = 6)
);

CREATE TABLE HABITACIONES (
  NUMERO_HABITACION INT NOT NULL,
  ID_HOTEL CHAR(6) NOT NULL,
  TIPO_HABITACION VARCHAR(10) NOT NULL,
  PRECIO_EXTRA INT,
  CONSTRAINT PK14 PRIMARY KEY (ID_HOTEL, NUMERO_HABITACION)
);

CREATE TABLE RESERVAS_HOTEL (
  ID_RESERVA CHAR(7) NOT NULL,
  ID_HOTEL CHAR(6) NOT NULL,
  NUMERO_HABITACION INT NOT NULL,
  CONSTRAINT PK6 PRIMARY KEY (ID_RESERVA, NUMERO_HABITACION),
  CONSTRAINT FK3 FOREIGN KEY (ID_RESERVA) REFERENCES RESERVAS (ID_RESERVA) ON DELETE CASCADE,
  CONSTRAINT FK4 FOREIGN KEY (ID_HOTEL) REFERENCES HOTELES (ID_HOTEL) ON DELETE CASCADE,
  CONSTRAINT FK5 FOREIGN KEY (ID_HOTEL, NUMERO_HABITACION) REFERENCES HABITACIONES (ID_HOTEL, NUMERO_HABITACION) ON DELETE CASCADE
);

CREATE TABLE MODELOS_COCHE (
  MODELO_COCHE VARCHAR(30) NOT NULL,
  NUMERO_ASIENTOS INT NOT NULL,
  CONSTRAINT PK15 PRIMARY KEY (MODELO_COCHE)
);

CREATE TABLE COCHES (
  MATRICULA_COCHE CHAR(8) NOT NULL,
  MODELO_COCHE VARCHAR(30) NOT NULL,
  PRECIO_POR_DIA INT NOT NULL,
  AEROPUERTO VARCHAR(3) NOT NULL,
  CONSTRAINT PK13 PRIMARY KEY (MATRICULA_COCHE),
  CONSTRAINT FK15 FOREIGN KEY (MODELO_COCHE) REFERENCES MODELOS_COCHE (MODELO_COCHE) ON DELETE CASCADE,
  CONSTRAINT CHK_MATRICULA_COCHE_LENGTH CHECK (CHAR_LENGTH(MATRICULA_COCHE) = 8)
);

CREATE TABLE RESERVAS_COCHE (
  ID_RESERVA CHAR(7) NOT NULL,
  MATRICULA_COCHE CHAR(8),
  CONSTRAINT PK7 PRIMARY KEY (ID_RESERVA),
  CONSTRAINT FK7 FOREIGN KEY (ID_RESERVA) REFERENCES RESERVAS (ID_RESERVA) ON DELETE CASCADE,
  CONSTRAINT FK8 FOREIGN KEY (MATRICULA_COCHE) REFERENCES COCHES (MATRICULA_COCHE) ON DELETE CASCADE
);

CREATE TABLE VUELOS (
  ID_VUELO INT NOT NULL,
  ID_TRAYECTO VARCHAR(7) NOT NULL,
  MATRICULA_AVION CHAR(5) NOT NULL,
  FECHA_VUELO DATE NOT NULL,
  CONSTRAINT PK9 PRIMARY KEY (ID_VUELO),
  CONSTRAINT FK12 FOREIGN KEY (ID_TRAYECTO) REFERENCES TRAYECTOS (ID_TRAYECTO) ON DELETE CASCADE,
  CONSTRAINT FK13 FOREIGN KEY (MATRICULA_AVION) REFERENCES AVIONES (MATRICULA_AVION) ON DELETE CASCADE
);

CREATE TABLE RESERVAS_AVION (
  ID_VUELO INT NOT NULL,
  ID_RESERVA CHAR(7) NOT NULL,
  NUMERO_BILLETE CHAR(11) NOT NULL,
  NUMERO_ASIENTO VARCHAR(3),
  CONSTRAINT PK8 PRIMARY KEY (ID_RESERVA, ID_VUELO),
  CONSTRAINT IND1 UNIQUE (NUMERO_BILLETE),
  CONSTRAINT FK9 FOREIGN KEY (ID_RESERVA) REFERENCES RESERVAS (ID_RESERVA) ON DELETE CASCADE,
  CONSTRAINT FK10 FOREIGN KEY (ID_VUELO) REFERENCES VUELOS (ID_VUELO) ON DELETE CASCADE,
  CONSTRAINT FK11 FOREIGN KEY (NUMERO_ASIENTO) REFERENCES ASIENTOS (NUMERO_ASIENTO) ON DELETE CASCADE
);