from datetime import datetime
import logging
import random
import socket
import time
import signal
import configparser
import os
import sys
import threading

# Archivo de configuración
CONFIG_FILE = "config.conf"

# Si no pasamos nada como parámetro -> tcp_flood.log
# Si le pasamos algo como parámetro -> definimos el nombre del archivo de log
# Cuando lo llamamos desde global_flood, le pasamos a todos los scripts el mismo archivo de log
now = datetime.now()
if len(sys.argv) > 1:
    log_filename = sys.argv[1]
else:
    log_filename = f"tcp_flood_{now.day:02d}_{now.month:02d}__{now.hour:02d}_{now.minute:02d}.log"

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

# Array de Hebras Activas
threads_active = []

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
    print("\nInterrupción detectada. Deteniendo el flood TCP...")
    running = False  # Cambiar la variable para detener el envío de datos

signal.signal(signal.SIGINT, signal_handler)

def connect_socket(host, port):
    """Establece conexión TCP con el servidor."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print(f"Conectado a {host}:{port}")
    return s

def send_tcp(host, port, data, speed, end_time):
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    packet_size = len(data)
    delay = packet_size / speed    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            while running and time.time() < end_time:
                s.sendall(data)
                time.sleep(delay)
    except Exception as e:
        print(f"[ERROR] {e}")

def flood_thread(host, port, data, speed, end_time):
    packet_size = len(data)
    delay = packet_size / speed
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            while running and time.time() < end_time:
                s.sendall(data)
                time.sleep(delay)
    except Exception as e:
        print(f"[ERROR] {e}")





def flood_tcp_speed_with_connect(host, port, packet_size, threads, speed, duration):

    try:
        # s = connect_socket(host, port)

        # Crear paquete de datos de prueba
        data = b'A' * packet_size  # Tamaño pasado como parámetro en config.conf
        speed_with_threads = speed/threads

        logger.info(f"Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")
        
        threads_active = []
        for _ in range(threads):
            thread = threading.Thread(target=send_tcp, args=(host, port, data, speed_with_threads, duration))
            threads_active.append(thread)
            thread.start()
        for thread in threads_active:
            thread.join()
      

        print("Flood TCP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")


# Flood TCP a la velocidad pasada como parámetro.
# No hacemos connect, puesto que le hacemos anteriormente en la función que le llama
def flood_tcp_speed(host, port, packet_size, threads, speed, duration):

    threads_active = []
    speed_with_threads = speed / threads
    data = b'A' * packet_size  # Tamaño pasado como parámetro en config.conf

    logger.info(f"Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")    
    print(time.time())
    
    end_time = time.time() + duration

    for _ in range(threads):
        t = threading.Thread(target=send_tcp, args=(host, port, data, speed_with_threads, end_time,))
        t.start()
        threads_active.append(t)

    for t in threads_active:
        t.join()

    """ s = connect_socket(host, port)

    # Crear paquete de datos de prueba
    data = b'A' * packet_size  # Tamaño pasado como parámetro en config.conf
    speed_with_threads = speed / threads

    print(f"[LOG] Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")

    threads_active = []
    def worker():
        send_tcp(host, port, data, speed_with_threads, duration)

    for _ in range(threads):
        thread = threading.Thread(target=send_tcp2, args=(s, host, port, data, speed_with_threads, duration))
        threads_active.append(thread)
        thread.start()
    for thread in threads_active:
        thread.join()

    s.close() """        

    

def flood_tcp_speed_series(host, port, packet_size, threads, speed_list, duration_list):

    try:
        s = connect_socket(host, port)

        if len(speed_list) != len(duration_list):
            raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")

        for i in range(len(speed_list)):
            speed = speed_list[i]
            duration = duration_list[i]

            # print(f"\n--- Iniciando etapa {i+1} ---")
            # print(f"Enviando a {speed} Bytes/s durante {duration} segundos")

            flood_tcp_speed(host, port, packet_size, threads, speed, duration)

        s.close()
        # print("\nFlood TCP finalizado.")

    except Exception as e:
        print(f"Error en la conexión: {e}")


def flood_tcp_speed_series_transition(host, port, packet_size, threads, speed_list, duration_list, time_transition, num_transition):

    try:
        # s = connect_socket(host, port)

        if len(speed_list) != len(duration_list):
            raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
        
        duration_incr = time_transition / num_transition # Duracion de cada etapa de transición entre cada Velocidad del Array

        for i in range(len(speed_list)):
            speed = speed_list[i]
            duration = duration_list[i]

            # print(f"\n--- Iniciando etapa {i+1} ---")
            # print(f"Enviando a {speed} Bytes/s durante {duration} segundos")

            flood_tcp_speed(host, port, packet_size, threads, speed, duration)

            if i < (len(speed_list) - 1):
                # print("Iniciando etapa de transición de incremento de velocidad")
                speed_next = speed_list[i+1]
                increase_speed = (speed_next - speed) / num_transition
                count = 0
                time_actual = time.time()
                time_end = time_actual + time_transition
                while speed < speed_next:
                    count += 1
                    speed += increase_speed
                    flood_tcp_speed(host, port, packet_size, threads, speed, duration_incr)

        # s.close()
        print("\nFlood TCP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")

def flood_tcp_random(host, port, packet_size, threads, speed_list, duration_list, time_transition_random, max_size_transition):

    try:
        # s = connect_socket(host, port)

        print(speed_list)
        print(duration_list)

        for i in range(len(speed_list)):
            speed = speed_list[i]
            duration = duration_list[i]

            flood_tcp_speed(host, port, packet_size, threads, speed, duration)

            if i < (len(speed_list) - 1):

                speed_next = speed_list[i+1]
                
                # print(f"\n--- Iniciando etapa {i+1} ---")
                # print(f"Tamaño del paquete ARP: {packet_size} bytes")
                # print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos con {threads} hilos")

                while(abs(speed_next - speed) > max_size_transition):
                    if(speed_next > speed):
                        speed += max_size_transition
                        flood_tcp_speed(host, port, packet_size, threads, speed, time_transition_random)
                    else: 
                        speed -= max_size_transition
                        flood_tcp_speed(host, port, packet_size, threads, speed, time_transition_random)

        # s.close() 

        print("\nFlood TCP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")

if __name__ == "__main__":

    if not os.path.exists(CONFIG_FILE):
        print(f"Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        sys.exit(1)
        

    # LEEMOS EL ARCHIVO CONFIG
    config = load_config(CONFIG_FILE)
    
    # LEEMOS LOS PARÁMETROS DEL ARCHIVO CONFIG


    server_ip = config.get('server_ip_TCP')
    server_port = int(config.get('server_port_TCP'))
    packet_size = int(config.get('packet_size_TCP'))
    threads = int(config.get('threads_TCP'))

    generacion_random = int(config.get('generacion_random_TCP'))

    if (generacion_random==1):
        num_generaciones = int(config.get('num_generaciones_TCP'))
        speed_min = int(config.get('speed_min_TCP'))
        speed_max = int(config.get('speed_max_TCP'))
        duration_min = int(config.get('duration_min_TCP'))
        duration_max = int(config.get('duration_max_TCP'))
        time_transition_random = int(config.get('time_transition_random_TCP'))
        max_size_transition = int(config.get('max_size_transition_TCP'))

        speed_list = [random.randint(speed_min, speed_max) for _ in range(num_generaciones)]
        duration_list = [random.randint(duration_min, duration_max) for _ in range(num_generaciones)]

        flood_tcp_random(server_ip, server_port, packet_size, threads, speed_list, duration_list, time_transition_random, max_size_transition)

    else:
    
        speed_list = list(map(int, config.get('speed_list_TCP').split(','))) # Velocidades en Bytes/s
        duration_list = list(map(int, config.get('duration_list_TCP').split(',')))  # Duraciones en segundos 
        time_transition = int(config.get('time_transition_TCP'))
        num_transition = int(config.get('num_transition_TCP')) 

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
            flood_tcp_speed(server_ip, server_port, packet_size, threads, speed_list, duration_list)
        elif time_transition > 0 and num_transition <= 0:
            print(f"time_transition tiene un valor correcto pero num_transion NO -> num_transition = {num_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_tcp_speed_series(server_ip, server_port, packet_size, speed_list, duration_list)
        elif num_transition > 0 and time_transition <= 0:
            print(f"num_transition tiene un valor correcto pero time_transition NO -> time_transition = {time_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_tcp_speed_series(server_ip, server_port, packet_size, speed_list, duration_list)
        else:
            flood_tcp_speed_series_transition(server_ip, server_port, packet_size, speed_list, duration_list, time_transition, num_transition)



