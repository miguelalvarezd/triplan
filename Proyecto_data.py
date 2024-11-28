def RellenarAeropuertos():
    print('hola')
    #leemos csv y creamos dic
    aeropuertos = {}

    return aeropuertos


def ReservarBillete(reserva):
    trayecto = 0

    print('\Iniciamos una reserva de vuelo!')
    aeropuertos = RellenarAeropuertos()

    while(trayecto):
        #Imprimir lista aeropuertos
        origen = input('Introduzca el codigo (AAA) de la ciudad de origen: ')
        destino = input('Introduzca el codigo (AAA) de la ciudad de destino: ')

        #SEELCT buscar trayecto compatible en destino y origen
        #SI NO hay trayecto disponible
        print('Lo siento, no operamos vuelos desde {} hasta {}'.format(aeropuertos[origen], aeropuertos[destino])) 
        decision = input('¿Quiere buscar otra posibilidad de vuelo? (S/N)')

        if(decision == 'N'):
            trayecto = 0

        elif(decision == 'S'):
            trayecto = 1
        
    #SI HAY trayecto compatible
    reserva['origen'] = origen
    reserva['destino'] = destino

    #hacemos un SELECT de las horas compatibles con ese origen y destino y printeamos
    print('HORAS DISPONIBLES')

    reserva['hora_vuelo'] = input('')
    #precio_base =

    #pedimos clase del billete de avión
    #Checker clases que estan libres y printearlas junto con su precio extra
    reserva['clase'] = input('Elija una clase de billete: ')
    #precio_extra =

    #calculamos el precio total
    reserva['precio'] = 100 #precio_base + precio_extra

    #preguntamos por vuelo de vuelta
    
          




def ReservarHotel(reserva):
    print('\nVamos a reservar una habitación!')


def ReservarCoche(reserva):
    print('\nVamos a reservar un coche!')
    

def main():

    print('Bienvenido a Elefantes!!')
    print('Escoja qué número corresponde a su rol por favor: ')
    print('1- Cliente')
    print('2- Empleado')
    rol = int(input(''))

    match rol:
        case 1:
            #todo cliente
            first_time = input('¿Es la primera vez que usa nuestra plataforma? (S/N): ')
            cliente = {}

            inicio = 0
            while(not inicio):
                match first_time:
                    case 'S': #registrarse
                        #Rellenamos los datos del cliente porque es un nuevo cliente 
                        cliente['dni'] = input('\nIntroduzca su dni: ').upper()
                        cliente['nombre'] = input('Introduzca su nombre de pila: ').upper()
                        cliente['telefono'] = int(input('Introduzca su telefono: (6 digitos sin separación) '))
                        cliente['tier'] = 'BRONZE'

                        #añadimos los datos recogidos a la db
    
                        inicio = 1 

                    case 'N': #iniciar sesion
                        #necesitamos identificar cliente
                        cliente['dni'] = input('Introduzca su dni: ').upper()

                        #buscar ese dni en DB y comprobar que existe --> SELECT
                
                        #guardamos nombre, telefono y tier del dni si es que existe
                        inicio = 1

                        #si el DNI no existe pedimos que se registre ya que será un cliente nuevo
                        first_time = 'S'

                    case _:
                        print('Elija una opción correcta por favor')

            print('\n\nBienvenido {}'.format(cliente['nombre']))

            #Empezamos una reserva
            tipo_reserva = int(input('¿Qué tipo de reserva quiere hacer primero? (Escoja un número): \n1-Avión\n2-Hotel\n3-Coche'))
            reserva = {}
            reserva 

            print('En qué fecha requiere nuestros servicios?')
            reserva['fecha_inicio'] = input('Fecha de inicio (YYYY-MM-DD):')
            reserva['fecha_final']= input('Fecha de fin (YYYY-MM-DD):')

            match tipo_reserva:
                case 1: #reserva un billete de avión

                    ReservarBillete(reserva)
                
                case 2: #reserva una habitación de hotel
                    ReservarHotel(reserva)

                case 3: #reserva un coche
                    ReservarCoche(reserva)


        case 2:
            #empleados --> verificación con contraseña
            password = input('\nIntroduzca la contraseña para empleados:')

            while(password != 'elefantes'):
                password = input('Contraseña incorrecta, por favor inténtelo de nuevo:')

            print('\nContraseña correcta')
            

if __name__ == '__main__':
    main()