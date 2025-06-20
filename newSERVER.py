import socket
import threading

HOST = '192.168.56.101'
PORT = 12345
PACKET_SIZE = 100

def handle_tcp_client(conn, addr):
    """Maneja una conexión TCP individual."""
    print(f"[TCP] Conexión TCP establecida desde {addr}")
    with conn:
        while True:
            data = conn.recv(PACKET_SIZE)
            if not data:
                break
            print(f"[TCP] [{addr}] Recibido {len(data)} bytes")
    print(f"[TCP] Conexión cerrada con {addr}")

def tcp_server():
    """Servidor TCP que acepta múltiples clientes en hilos separados."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[TCP] Servidor escuchando en {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True)
            thread.start()

def udp_server():
    """Servidor para manejar conexiones UDP."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Aumentar el tamaño del buffer de recepción
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**20)  # 1 MB
    
    # Timeout para evitar bloqueo infinito
    udp_socket.settimeout(3.0)
    
    udp_socket.bind((HOST, PORT))
    print(f"[UDP] Servidor escuchando en {HOST}:{PORT}")

    while True:
        try:
            data, addr = udp_socket.recvfrom(PACKET_SIZE)
            print(f"[UDP] Recibido {len(data)} bytes de {addr}")
        except socket.timeout:
            print("[UDP] Timeout: no se recibieron datos en 3 segundos")
        except Exception as e:
            print(f"[UDP] Error: {e}")

def main():
    # Crear hilos para servidores TCP y UDP
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    udp_thread = threading.Thread(target=udp_server, daemon=True)

    tcp_thread.start()
    udp_thread.start()

    print("[INFO] Servidor híbrido TCP/UDP en ejecución. Presiona Ctrl+C para detener.")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido.")

if __name__ == "__main__":
    main()
