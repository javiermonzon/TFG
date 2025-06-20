
import matplotlib.pyplot as plt
import datetime
import re
import sys

# Leer archivo pasado como argumento
if len(sys.argv) != 2:
    print("Uso: python graficar_flood.py arp_flood.log")
    sys.exit(1)

log_file = sys.argv[1]

# Expresión regular para extraer fecha y bitrate
log_pattern = re.compile(
    r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[INFO\] Se va a emitir a un Bitrate de (?P<bitrate>[\d.]+) KBps')

timestamps = []
bitrates = []

with open(log_file, 'r') as f:
    for line in f:
        match = log_pattern.search(line)
        if match:
            ts_str = match.group("timestamp")
            bitrate = float(match.group("bitrate"))

            ts = datetime.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            timestamps.append(ts)
            bitrates.append(bitrate)

if not timestamps:
    print("No se encontraron registros válidos en el log.")
    sys.exit(1)

# Graficar
plt.figure(figsize=(10, 5))
plt.plot(timestamps, bitrates, marker='o', linestyle='-', color='blue')
plt.title("Bitrate del ARP Flood en el Tiempo")
plt.xlabel("Tiempo")
plt.ylabel("Bitrate (KBps)")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Guardar gráfica en archivo PNG
output_file = "grafica_flood.png"
plt.savefig(output_file)
print(f"Gráfica guardada como '{output_file}'")
