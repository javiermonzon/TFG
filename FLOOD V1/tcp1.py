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

    def connect_socket():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        print(f"Conectado a {host}:{port}")
        return s

    s = connect_socket()

    # Datos a enviar: un paquete de 10 KB (10240 bytes)
    data = b'A' *10240  # 10 KB de datos

    # Limitar el ancho de banda 
    bytes_per_second = 2 * 1024  
    interval = len(data) / bytes_per_second  # Tiempo entre envíos de paquetes

    start_time = time.time()

    while running:
        try:
            # Enviar datos
            s.sendall(data)
            print(f"Enviado {len(data)} bytes al servidor")

            # Recibir ACK
            response = s.recv(1024)  # Leer respuesta del servidor
            if response == b"ACK":
                print(f"Recibido ACK desde {host}:{port}")
            else:
                print(f"Respuesta inesperada del servidor: {response}")

        except (ConnectionResetError, BrokenPipeError):
            print("Error de conexión. Intentando reconectar...")
            s.close()
            s = connect_socket()

        time.sleep(interval)  # Controlar el intervalo para mantener el ancho de banda

        # Limitar el tiempo de ejecución a 8 segundos
        if time.time() - start_time > 8:
            break

    s.close()
    print("Conexión cerrada")

if __name__ == '__main__':
    client()
