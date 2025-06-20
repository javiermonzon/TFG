import socket
import threading

def tcp_server(host, port):
    """Servidor para manejar conexiones TCP."""
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen(5)
    print(f"Servidor TCP escuchando en {host}:{port}")

    while True:
        conn, addr = tcp_socket.accept()
        print(f"Conexión TCP establecida con {addr}")
        try:
            while True:
                data = conn.recv(10240)  # Recibir datos
                if not data:
                    break
                print(f"Recibido {len(data)} bytes de {addr} (TCP)")
                conn.sendall(b"ACK")  # Responder con ACK
        except ConnectionResetError:
            print(f"Conexión TCP perdida con {addr}")
        finally:
            conn.close()
            print(f"Conexión TCP cerrada con {addr}")


def udp_server(host, port):
    """Servidor para manejar conexiones UDP."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print(f"Servidor UDP escuchando en {host}:{port}")

    while True:
        try:
            data, addr = udp_socket.recvfrom(10240)  # Recibir datos UDP
            print(f"Recibido {len(data)} bytes de {addr} (UDP)")
            udp_socket.sendto(b"ACK", addr)  # Responder con ACK
        except Exception as e:
            print(f"Error en UDP: {e}")


def main():
    host = '192.168.56.101'  # Dirección IP del servidor
    port = 12345  # Puerto compartido para TCP y UDP

    # Crear hilos para los servidores TCP y UDP
    tcp_thread = threading.Thread(target=tcp_server, args=(host, port), daemon=True)
    udp_thread = threading.Thread(target=udp_server, args=(host, port), daemon=True)

    # Iniciar ambos servidores
    tcp_thread.start()
    udp_thread.start()

    print("Servidor híbrido TCP/UDP en ejecución. Presiona Ctrl+C para detener.")

    # Mantener el programa principal corriendo
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == '__main__':
    main()
