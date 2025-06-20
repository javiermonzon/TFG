from datetime import datetime
import logging
import random
import socket
import time
import signal
import configparser
import os
import sys

# Archivo de configuración
CONFIG_FILE = "config.conf"

# Si no pasamos nada como parámetro -> udp_flood.log
# Si le pasamos algo como parámetro -> definimos el nombre del archivo de log
# Cuando lo llamamos desde global_flood, le pasamos a todos los scripts el mismo archivo de log
now = datetime.now()
if len(sys.argv) > 1:
    log_filename = sys.argv[1]
else:
    log_filename = f"udp_flood_{now.day:02d}_{now.month:02d}__{now.hour:02d}_{now.minute:02d}.log"

# Crear el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Formato del log
# formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S') -> No quiero que me saque el [INFO]
formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Handler para archivo
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para consola (terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Variable global para controlar si se debe detener el envío
running = True

# Leer configuración desde el archivo
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['DEFAULT']  # Leer la sección DEFAULT

def signal_handler(sig, frame):
    """
    Manejador de señal para SIGINT (Ctrl+C).
    Detener el cliente de manera segura.
    """
    global running
    print("\nInterrupción detectada. Deteniendo el flood UDP...")
    running = False  # Cambiar la variable para detener el envío de datos

signal.signal(signal.SIGINT, signal_handler)


def flood_udp_speed_with_connect(host, port, packet_size, speed, duration):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Crear paquete de datos de prueba
        # data = b'A' * 1024  # 1 KB por paquete
        data = b'A' * packet_size
        packet_size = len(data)
        delay = packet_size / speed  # Intervalo de envío para respetar la velocidad

        # print(f"Iniciando flood UDP a {speed} Bytes/s durante {duration} segundos...")

        end_time = time.time() + duration

        logger.info(f"Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")

        while running and time.time() < end_time:
            s.sendto(data, (host, port))  # Enviar datos

            time.sleep(delay)  # Control de velocidad


        s.close()
        print("Flood UDP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")




def flood_udp_speed(host, port, packet_size, speed, duration):
    """
    Realiza un flood UDP enviando datos a una velocidad específica durante un tiempo determinado.
    
    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed: velocidad en Bytes/s
    - duration: duración en segundos
    """
    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Crear paquete de datos de prueba
        # data = b'A' * 10240  # 10 KB por paquete
        data = b'A' * packet_size
        packet_size = len(data)
        delay = packet_size / speed  # Intervalo de envío para respetar la velocidad

        # print(f"Iniciando flood UDP a {speed} Bytes/s durante {duration} segundos...")

        end_time = time.time() + duration

        logger.info(f"Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")

        while running and time.time() < end_time:
            s.sendto(data, (host, port))  # Enviar datos
            time.sleep(delay)  # Control de velocidad

        s.close()
    
    except Exception as e:
        print(f"Error en la conexión: {e}")

    

    

def flood_udp_speed_series(host, port, packet_size, speed_list, duration_list):
    """
    Ejecuta un flood UDP con diferentes velocidades y duraciones de forma secuencial.

    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed_list: Lista de velocidades en Bytes/s
    - duration_list: Lista de duraciones en segundos
    """
    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if len(speed_list) != len(duration_list):
            raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
        

        for i in range(len(speed_list)):
            speed = speed_list[i]
            duration = duration_list[i]

            # print(f"\n--- Iniciando etapa {i+1} ---")
            # print(f"\nEnviando a {speed} Bytes/s durante {duration} segundos")

            flood_udp_speed(host, port, packet_size, speed, duration)
        
        s.close()
        print("Flood UDP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")



    print("\nFlood UDP finalizado.")



def flood_udp_speed_series_transition(host, port, packet_size, speed_list, duration_list, time_transition, num_transition):
    """
    Ejecuta un flood UDP con diferentes velocidades y duraciones de forma secuencial.

    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed_list: Lista de velocidades en Bytes/s
    - duration_list: Lista de duraciones en segundos
    """
    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if len(speed_list) != len(duration_list):
            raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
        
        duration_incr = time_transition / num_transition # Duracion de cada etapa de transición entre cada Velocidad del Array

        for i in range(len(speed_list)):
            speed = speed_list[i]
            duration = duration_list[i]

            

            # print(f"\n--- Iniciando etapa {i+1} ---")
            # print(f"\nEnviando a {speed} Bytes/s durante {duration} segundos")

            flood_udp_speed(host, port, packet_size, speed, duration)
            
            if i < (len(speed_list) - 1):
                speed_next = speed_list[i+1]
                increase_speed = (speed_next - speed) / num_transition
                count = 0
                time_actual = time.time()
                time_end = time_actual + time_transition
                while speed < speed_next:
                    count += 1
                    speed += increase_speed
                    # print(f"\n--- Iniciando etapa de incremento {count} ---")
                    # print(f"\nEnviando a {speed} Bytes/s durante {duration_incr} segundos")
                    flood_udp_speed(host, port, packet_size, speed, duration_incr)
        
        s.close()
        print("Flood UDP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")



    print("\nFlood UDP finalizado.")


def flood_udp_random(host, port, packet_size, speed_list, duration_list, time_transition_random, max_size_transition):

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print(speed_list)
        print(duration_list)

        for i in range(len(speed_list)):
            speed = speed_list[i]
            duration = duration_list[i]

            flood_udp_speed(host, port, packet_size, speed, duration)

            if i < (len(speed_list) - 1):

                speed_next = speed_list[i+1]
                
                # print(f"\n--- Iniciando etapa {i+1} ---")
                # print(f"Tamaño del paquete ARP: {packet_size} bytes")
                # print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos con {threads} hilos")

                while(abs(speed_next - speed) > max_size_transition):
                    if(speed_next > speed):
                        speed += max_size_transition
                        flood_udp_speed(host, port, packet_size, speed, time_transition_random)
                    else: 
                        speed -= max_size_transition
                        flood_udp_speed(host, port, packet_size, speed, time_transition_random)

        s.close() 

        print("\nFlood UDP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")

    

if __name__ == "__main__":

    if not os.path.exists(CONFIG_FILE):
        print(f"Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        sys.exit(1)

    # LEEMOS EL ARCHIVO CONFIG
    config = load_config(CONFIG_FILE)
    
    # LEEMOS LOS PARÁMETROS DEL ARCHIVO CONFIG


    server_ip = config.get('server_ip_UDP')
    server_port = int(config.get('server_port_UDP'))
    packet_size = int(config.get('packet_size_UDP'))

    generacion_random = int(config.get('generacion_random_UDP'))

    if (generacion_random==1):
        num_generaciones = int(config.get('num_generaciones_UDP'))
        speed_min = int(config.get('speed_min_UDP'))
        speed_max = int(config.get('speed_max_UDP'))
        duration_min = int(config.get('duration_min_UDP'))
        duration_max = int(config.get('duration_max_UDP'))
        time_transition_random = int(config.get('time_transition_random_UDP'))
        max_size_transition = int(config.get('max_size_transition_UDP'))

        speed_list = [random.randint(speed_min, speed_max) for _ in range(num_generaciones)]
        duration_list = [random.randint(duration_min, duration_max) for _ in range(num_generaciones)]

        flood_udp_random(server_ip, server_port, packet_size, speed_list, duration_list, time_transition_random, max_size_transition)
    
    else:
        speed_list = list(map(int, config.get('speed_list_UDP').split(','))) # Velocidades en Bytes/s
        duration_list = list(map(int, config.get('duration_list_UDP').split(',')))  # Duraciones en segundos 
        time_transition = int(config.get('time_transition_UDP'))
        num_transition = int(config.get('num_transition_UDP')) 


        if len(speed_list) != len(duration_list):
            print("Tamaño del array speed_list:")
            print(f"len(speed_list) = {len(speed_list)}")
            print("\nTamaño del array duration_list:")
            print(f"len(duration_list) = {len(duration_list)}")
            raise ValueError("\nLas listas de velocidad y duración deben tener el mismo tamaño")
        
        for i in range(len(speed_list)):
            if speed_list[i] <= 0:
                print(f"speed_list[{i}] = {speed_list[i]}")
                raise ValueError("\nLos valores de velocidad de envío (SPEED_LIST) deben ser positivos (mayores que 0)")
            elif duration_list[i] <= 0:
                print(f"duration_list[{i}] = {duration_list[i]}")
                raise ValueError("\nLos valores de duración de envío (DURATION_LIST) deben ser positivos (mayores que 0)")
            
        if len(speed_list) == 1:
            flood_udp_speed(server_ip, server_port, speed_list, duration_list)
        elif time_transition > 0 and num_transition <= 0:
            print(f"time_transition tiene un valor correcto pero num_transion NO -> num_transition = {num_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_udp_speed_series(server_ip, server_port, speed_list, duration_list)
        elif num_transition > 0 and time_transition <= 0:
            print(f"num_transition tiene un valor correcto pero time_transition NO -> time_transition = {time_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_udp_speed_series(server_ip, server_port, speed_list, duration_list)
        else:
            flood_udp_speed_series_transition(server_ip, server_port, speed_list, duration_list, time_transition, num_transition)
