# Torno Divisor CNC Controlado por WiFi

![Interfaz Web del Torno Divisor](https://ejemplo.com/torno-divisor.jpg) <!-- Reemplaza con tu imagen -->

Sistema completo para controlar un torno divisor CNC mediante una interfaz web, con precisión de micropasos y control de velocidad.

## Características Principales

- ✅ **Control preciso**: Resolución de 0.1125° (200 pasos/rev + 16 micropasos)
- 📶 **Interfaz WiFi**: Access Point integrado (IP: 192.168.4.1)
- 🖥️ **Panel de control web**: Interfaz responsive desde cualquier dispositivo
- ⚡ **Control de velocidad**: 1-300 RPM ajustables
- 🛑 **Parada de emergencia**: Corte físico del motor
- 🔄 **División automática**: Cálculo preciso de divisiones del círculo

## Especificaciones Técnicas

| Parámetro           | Valor               |
|---------------------|---------------------|
| Motor               | NEMA 23 (1.8°/paso) |
| Microstepping       | 1/16                |
| Resolución angular  | 0.1125°             |
| Velocidad máxima    | 300 RPM             |
| Precisión mínima    | 0.1125°             |
| Conexión            | WiFi AP (802.11n)   |
| Voltaje operación   | 12-24V DC           |
| Consumo máximo      | 2A                  |

## Hardware Requerido

- Placa ESP32 o ESP8266
- Driver de motor paso a paso (A4988 o DRV8825)
- Fuente de alimentación 12-24V DC
- Motor NEMA 23
- Cables y conectores

## Instalación

1. **Cargar el firmware**:
   ```bash
   pip install esptool
   esptool.py --port /dev/ttyUSB0 write_flash 0x0 firmware.bin

2. **Subir archivos al sistema de archivos:**
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put motor.py
ampy --port /dev/ttyUSB0 put server.py
ampy --port /dev/ttyUSB0 put -r static/
3. **Conectar hardware:**
GPIO19 → DIR
GPIO23 → STEP
GPIO18 → ENABLE
GND → Tierra común

## Uso
1. Conectarse al WiFi TornoDivisor (contraseña: torno1234)

2. Abrir navegador en http://192.168.4.1

3. Operaciones disponibles:

- Movimiento angular preciso (0.1125°)
- División automática del círculo
- Ajuste de velocidad (1-300 RPM)
- Parada de emergencia
- Reinicio a posición cero
## Estructura de Archivos

/torno-divisor/
├── config.py         # Configuración WiFi y motor
├── main.py           # Punto de entrada
├── motor.py          # Control del motor
├── server.py         # Servidor web
└── static/
    ├── index.html    # Interfaz web
    ├── style.css     # Estilos
    └── script.js     # Lógica frontend
