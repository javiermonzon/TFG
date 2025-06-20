import socket
import time
import signal

# Variable global para controlar si se debe detener el envío
running = True

def signal_handler(sig, frame):
    """
    Manejador de señal para SIGINT (Ctrl+C).
    Detener el cliente de manera segura.
    """
    global running
    print("\nInterrupción detectada. Deteniendo el cliente...")
    running = False  # Cambiar la variable para detener el envío de datos

signal.signal(signal.SIGINT, signal_handler)

def client():
    host = '192.168.56.101'  # Dirección IP del servidor
    port = 12345  # Puerto al que conectarse

    # Crear un socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Cliente conectado a {host}:{port}")

    # Datos a enviar: un paquete de 1024 bytes
    data = b'A' * 1024  # 1 KB de datos

    # Limitar el ancho de banda a 10 Mbps (aproximadamente 1.25 MB/s)
    bytes_per_second = 1 * 1024  # 1 Kbps
    interval = len(data) / bytes_per_second  # Tiempo entre envíos de paquetes

    start_time = time.time()
    while running:
        try:
            # Enviar datos al servidor
            s.sendto(data, (host, port))
            print(f"Enviado {len(data)} bytes al servidor")

            # Intentar recibir la respuesta ACK del servidor
            s.settimeout(2)  # Tiempo de espera para la respuesta (2 segundos)
            try:
                response, server_addr = s.recvfrom(1024)  # Leer respuesta
                if response == b"ACK":
                    print(f"Recibido ACK desde {server_addr}")
                else:
                    print(f"Respuesta inesperada: {response}")
            except socket.timeout:
                print("No se recibió respuesta del servidor (timeout).")

        except Exception as e:
            print(f"Error al enviar datos: {e}")

        time.sleep(interval)  # Controlar el intervalo para mantener el ancho de banda

        # Limitar el tiempo de ejecución a 60 segundos
        if time.time() - start_time > 5:
            break

    s.close()
    print("Conexión cerrada")

if __name__ == '__main__':
    client()
