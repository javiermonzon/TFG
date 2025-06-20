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
    print("\nInterrupción detectada. Deteniendo el flood TCP...")
    running = False  # Cambiar la variable para detener el envío de datos

signal.signal(signal.SIGINT, signal_handler)

def connect_socket(host, port):
    """Establece conexión TCP con el servidor."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print(f"Conectado a {host}:{port}")
    return s

def flood_tcp_speed(host, port, speed, duration):
    """
    Realiza un flood TCP enviando datos a una velocidad específica durante un tiempo determinado.
    
    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed: velocidad en Bytes/s
    - duration: duración en segundos
    """
    try:
        s = connect_socket(host, port)

        # Crear paquete de datos de prueba
        data = b'A' * 10240  # 10 KB por paquete
        packet_size = len(data)
        delay = packet_size / speed  # Intervalo de envío para respetar la velocidad

        print(f"Iniciando flood TCP a {speed} Bytes/s durante {duration} segundos...")

        end_time = time.time() + duration
        count = 0

        while running and time.time() < end_time:
            s.sendall(data)  # Enviar datos
            print(f"Paquete {count}. Enviado {packet_size} bytes")
            count +=1

            # Recibir ACK del servidor
            try:
                response = s.recv(1024)
                if response == b"ACK":
                    print("Recibido ACK")
                else:
                    print(f"Respuesta inesperada: {response}")
            except socket.timeout:
                print("No se recibió ACK a tiempo.")

            time.sleep(delay)  # Control de velocidad

        s.close()
        print("Flood TCP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")

def flood_tcp_speed_series(host, port, speed_list, duration_list):
    """
    Ejecuta un flood TCP con diferentes velocidades y duraciones de forma secuencial.

    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed_list: Lista de velocidades en Bytes/s
    - duration_list: Lista de duraciones en segundos
    """
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Enviando a {speed} Bytes/s durante {duration} segundos")

        flood_tcp_speed(host, port, speed, duration)

    print("\nFlood TCP finalizado.")


def flood_tcp_speed_series_transition(host, port, speed_list, duration_list, time_transition, num_transition):
    """
    Ejecuta un flood TCP con diferentes velocidades y duraciones de forma secuencial.

    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed_list: Lista de velocidades en Bytes/s
    - duration_list: Lista de duraciones en segundos
    """
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
    
    duration_incr = time_transition / num_transition # Duracion de cada etapa de transición entre cada Velocidad del Array

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"Enviando a {speed} Bytes/s durante {duration} segundos")

        flood_tcp_speed(host, port, speed, duration)

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
                flood_tcp_speed(host, port, speed, duration_incr)

    print("\nFlood TCP finalizado.")

if __name__ == "__main__":
    server_ip = "192.168.56.101"
    server_port = 12345

    speed_list = [5000, 10000, 20000]  # Velocidades en Bytes/s
    duration_list = [4, 4, 4]  # Duraciones en segundos

    time_transition = 15
    num_transition = 5

    flood_tcp_speed_series_transition(server_ip, server_port, speed_list, duration_list, time_transition, num_transition)
