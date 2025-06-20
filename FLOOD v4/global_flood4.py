import subprocess
import time
from datetime import datetime
import configparser
import os
import sys
import logging

# Archivo de configuración
CONFIG_FILE = "config.conf"

# Nombre del archivo de log
now = datetime.now()
log_filename = f"global_flood_{now.day:02d}_{now.month:02d}__{now.hour:02d}_{now.minute:02d}.log"

# Crear el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Formato del log
# formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S') -> No quiero que me saque el [INFO]
formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Handler para archivo
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para consola (terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Leer configuración desde el archivo
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['DEFAULT']  # Leer la sección DEFAULT

def do_list(variable):
    return list(map(int, config.get(variable).split(',')))

def execute_script(script_name):
    """
    Ejecutar un script y medir el tiempo de ejecución.
    """
    print(f"Ejecutando {script_name}...\n")  # Mensaje indicando que se está ejecutando el script

    start_EPOCH = time.time()  # EPOCH de arranque (tiempo de inicio en formato UNIX)
    start_time = datetime.fromtimestamp(start_EPOCH).strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora de arranque

    try:
        # Ejecutar el script de manera secuencial
        subprocess.run(['python3', script_name, log_filename], check=True)

        finish_EPOCH = time.time()  # EPOCH de parada (tiempo de fin en formato UNIX)
        finish_time = datetime.fromtimestamp(finish_EPOCH).strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora de parada

        # Calcular tiempo de ejecución
        execution_time = finish_EPOCH - start_EPOCH

        # Imprimir resultados con tabulación para alineación
        print(f"EPOCH arranque:\t\t{start_EPOCH:.2f}")
        print(f"EPOCH parada:\t\t{finish_EPOCH:.2f}")
        print(f"Time arranque:\t\t{start_time}")
        print(f"Time parada:\t\t{finish_time}")
        print(f"Tiempo de ejecución:\t{execution_time:.2f} segundos\n")  # Tiempo de ejecución en segundos

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_name}: {e}")

    except KeyboardInterrupt:
        finish_EPOCH = time.time()  # EPOCH de parada si se interrumpe con Ctrl + C
        finish_time = datetime.fromtimestamp(finish_EPOCH).strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora de parada

        # Calcular tiempo de ejecución
        execution_time = finish_EPOCH - start_EPOCH

        # Imprimir resultados con tabulación para alineación
        print(f"\nProceso interrumpido durante la ejecución de {script_name}.")
        print(f"EPOCH arranque:\t\t{start_EPOCH:.2f}")
        print(f"EPOCH parada:\t\t{finish_EPOCH:.2f}")
        print(f"Time arranque:\t\t{start_time}")
        print(f"Time parada:\t\t{finish_time}")
        print(f"Tiempo de ejecución hasta la interrupción:\t{execution_time:.2f} segundos\n")

if __name__ == "__main__":
    
    if not os.path.exists(CONFIG_FILE):
        print(f"Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        sys.exit(1)

    # LEEMOS EL ARCHIVO CONFIG
    config = load_config(CONFIG_FILE)
    
    # LEEMOS LOS PARÁMETROS DEL ARCHIVO CONFIG
    # Lista de scripts a ejecutar
    scripts = [s.strip() for s in config.get('scripts').split(',')]

    for script in scripts:
        execute_script(script)

