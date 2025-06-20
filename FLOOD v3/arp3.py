import socket
import struct
import threading
import sys
import signal
import os
import time
import configparser
import random
import logging

# Archivo de configuración
CONFIG_FILE = "config.conf"

# Array de Hebras Activas
threads_active = []


# Nombre del archivo de log
log_filename = "arp_flood.log"

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

# Leer configuración desde el archivo
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['DEFAULT']  # Leer la sección DEFAULT

def signal_handler(sig, frame):
    print("\nInterrupción detectada. Deteniendo todos los hilos...")
    for thread in threads_active:
        thread.join()
    sys.exit(0)

def create_arp_request(src_mac, src_ip, dst_ip):
    dst_mac = b'\xff\xff\xff\xff\xff\xff'
    eth_type = b'\x08\x06'
    hw_type = b'\x00\x01'
    proto_type = b'\x08\x00'
    hw_size = b'\x06'
    proto_size = b'\x04'
    opcode = b'\x00\x01'
    arp_src_mac = src_mac
    arp_src_ip = socket.inet_aton(src_ip)
    arp_dst_ip = socket.inet_aton(dst_ip)
    arp_frame = hw_type + proto_type + hw_size + proto_size + opcode + arp_src_mac + arp_src_ip + b'\x00\x00\x00\x00\x00\x00' + arp_dst_ip
    packet = dst_mac + src_mac + eth_type + arp_frame
    return packet

def send_arp(src_mac, src_ip, dst_ip, speed, duration):
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
    sock.bind((iface, 0))
    packet = create_arp_request(src_mac, src_ip, dst_ip)
    packet_size = len(packet)
    delay = packet_size / speed  # Intervalo de envío para respetar la velocidad
    end_time = time.time() + duration
    count = 1
    while time.time() < end_time:
        sock.send(packet)
        # print(f"Arp {count} enviado")
        time.sleep(delay)
        count +=1

def flood_arp(src_mac, src_ip, dst_ip, threads, speed, duration):
    speed_with_threads = speed / threads
    # print(f"[LOG] Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")
    logger.info(f"Se va a emitir a un Bitrate de {(speed/1000):.2f} KBps durante los próximos {duration} s.")
    def worker():
        send_arp(src_mac, src_ip, dst_ip, speed_with_threads, duration)
    threads_active = []
    for _ in range(threads):
        thread = threading.Thread(target=worker)
        threads_active.append(thread)
        thread.start()
    for thread in threads_active:
        thread.join()

def flood_arp_speed_series(src_mac, src_ip, dst_ip, threads, speed_list, duration_list):
   
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")

    # Crear un paquete de prueba para medir su tamaño en bytes
    test_packet = create_arp_request(src_mac, src_ip, dst_ip)
    packet_size = len(test_packet)  # Tamaño del paquete en bytes

    threads_active = []

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        speed_with_threads = speed / threads
        
        flood_arp(src_mac, src_ip, dst_ip, threads, speed, duration)


    print("\nFlood ARP finalizado.")


def flood_arp_speed_series_transition(src_mac, src_ip, dst_ip, threads, speed_list, duration_list, time_transition, num_transition):
    
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")

    # Crear un paquete de prueba para medir su tamaño en bytes
    test_packet = create_arp_request(src_mac, src_ip, dst_ip)
    packet_size = len(test_packet)  # Tamaño del paquete en bytes

    global threads_active

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        duration_incr = time_transition / num_transition # Duracion de cada etapa de transición entre cada Velocidad del Array

        """ print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Tamaño del paquete ARP: {packet_size} bytes")
        print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos con {threads} hilos") """

        flood_arp(src_mac, src_ip, dst_ip, threads, speed, duration)

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
                
                flood_arp(src_mac, src_ip, dst_ip, threads, speed, duration_incr)

    print("\nFlood ARP finalizado.\n")


def flood_arp_random(src_mac, src_ip, dst_ip, threads, speed_list, duration_list, time_transition_random, max_size_transition):

    global threads_active
    print(speed_list)
    print(duration_list)

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        flood_arp(src_mac, src_ip, dst_ip, threads, speed, duration)

        if i < (len(speed_list) - 1):

            speed_next = speed_list[i+1]
            
            while(abs(speed_next - speed) > max_size_transition):
                if(speed_next > speed):
                    speed += max_size_transition
                    flood_arp(src_mac, src_ip, dst_ip, threads, speed, time_transition_random) # 
                else: 
                    speed -= max_size_transition
                    flood_arp(src_mac, src_ip, dst_ip, threads, speed, time_transition_random)    

    print("\nFlood ARP finalizado.")


signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":

    if not os.path.exists(CONFIG_FILE):
        print(f"Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        sys.exit(1)

    # LEEMOS EL ARCHIVO CONFIG
    config = load_config(CONFIG_FILE)
    
    # LEEMOS LOS PARÁMETROS DEL ARCHIVO CONFIG
    source_ip = config.get('source_ip')
    target_ip = config.get('target_ip')
    iface = config.get('iface_ARP')
    source_mac = bytes.fromhex(config.get('source_mac_ARP').replace(':', ''))  # Ejemplo de MAC de origen
    threads = int(config.get('threads_ARP'))

    generacion_random = int(config.get('generacion_random_ARP'))

    if (generacion_random==1):
        num_generaciones = int(config.get('num_generaciones_ARP'))
        speed_min = int(config.get('speed_min_ARP'))
        speed_max = int(config.get('speed_max_ARP'))
        duration_min = int(config.get('duration_min_ARP'))
        duration_max = int(config.get('duration_max_ARP'))
        time_transition_random = int(config.get('time_transition_random_ARP'))
        max_size_transition = int(config.get('max_size_transition_ARP'))

        speed_list = [random.randint(speed_min, speed_max) for _ in range(num_generaciones)]
        duration_list = [random.randint(duration_min, duration_max) for _ in range(num_generaciones)]

        flood_arp_random(source_mac, source_ip, target_ip, threads, speed_list, duration_list, time_transition_random, max_size_transition)

    else:
        speed_list = list(map(int, config.get('speed_list_ARP').split(','))) # Velocidades en Bytes/s
        duration_list = list(map(int, config.get('duration_list_ARP').split(',')))  # Duraciones en segundos 
        time_transition = int(config.get('time_transition_ARP'))
        num_transition = int(config.get('num_transition_ARP')) 

  
        
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
            flood_arp(source_mac, source_ip, target_ip, threads, speed_list, duration_list)
        elif time_transition > 0 and num_transition <= 0:
            print(f"time_transition tiene un valor correcto pero num_transion NO -> num_transition = {num_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_arp_speed_series(source_mac, source_ip, target_ip, threads, speed_list, duration_list)
        elif num_transition > 0 and time_transition <= 0:
            print(f"num_transition tiene un valor correcto pero time_transition NO -> time_transition = {time_transition}")
            print("Se ejecutan las series sin transición entre ellas")
            flood_arp_speed_series(source_mac, source_ip, target_ip, threads, speed_list, duration_list)
        else:
            flood_arp_speed_series_transition(source_mac, source_ip, target_ip, threads, speed_list, duration_list, time_transition, num_transition)
