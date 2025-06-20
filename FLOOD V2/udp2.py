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
    print("\nInterrupción detectada. Deteniendo el flood UDP...")
    running = False  # Cambiar la variable para detener el envío de datos

signal.signal(signal.SIGINT, signal_handler)

def flood_udp_speed(host, port, speed, duration):
    """
    Realiza un flood UDP enviando datos a una velocidad específica durante un tiempo determinado.
    
    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed: velocidad en Bytes/s
    - duration: duración en segundos
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Crear paquete de datos de prueba
        # data = b'A' * 1024  # 1 KB por paquete
        data = b'A' * 1000
        packet_size = len(data)
        delay = packet_size / speed  # Intervalo de envío para respetar la velocidad

        print(f"Iniciando flood UDP a {speed} Bytes/s durante {duration} segundos...")

        end_time = time.time() + duration
        count = 1

        while running and time.time() < end_time:
            time_before = time.time()
            s.sendto(data, (host, port))  # Enviar datos
            time_after = time.time()
            print(f"Paquete {count}. Enviado {packet_size} bytes")
            t_packet = (time_after - time_before) * 10e6
            print(f"Tiempo entre paquetes: {t_packet} ns")
            count +=1
            time.sleep(delay)  # Control de velocidad


        s.close()
        print("Flood UDP finalizado.")
    
    except Exception as e:
        print(f"Error en la conexión: {e}")

def flood_udp_speed_series(host, port, speed_list, duration_list, time_transition, num_transition):
    """
    Ejecuta un flood UDP con diferentes velocidades y duraciones de forma secuencial.

    Parámetros:
    - host: IP del servidor
    - port: Puerto de conexión
    - speed_list: Lista de velocidades en Bytes/s
    - duration_list: Lista de duraciones en segundos
    """
    if len(speed_list) != len(duration_list):
        raise ValueError("Las listas de velocidad y duración deben tener el mismo tamaño")
    
    duration_incr = time_transition / num_transition

    for i in range(len(speed_list)):
        speed = speed_list[i]
        duration = duration_list[i]

        

        print(f"\n--- Iniciando etapa {i+1} ---")
        print(f"\nEnviando a {speed} Bytes/s durante {duration} segundos")

        flood_udp_speed(host, port, speed, duration)
        
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
                flood_udp_speed(host, port, speed, duration_incr)



    print("\nFlood UDP finalizado.")

    

if __name__ == "__main__":
    server_ip = "192.168.56.101"
    server_port = 12345

    speed_list = [5000, 10000, 20000]  # Velocidades en Bytes/s
    duration_list = [4, 4, 4]  # Duraciones en segundos
    time_transition = 10
    num_transition = 10

    flood_udp_speed_series(server_ip, server_port, speed_list, duration_list, time_transition, num_transition)
