# Configuración WiFi (Access Point)
WIFI_CONFIG = {
    'ap': {
        'ssid': 'TornoDivisor',
        'password': 'torno1234',
        'authmode': 3,  # WPA2
        'channel': 6,
        'timeout': 30  # Timeout en segundos
    }
}

# Configuración del Motor Paso a Paso
MOTOR_CONFIG = {
    'steps_per_rev': 200,      # Para motor NEMA 23 (1.8° por paso)
    'microsteps': 16,          # 1/16 de paso
    'max_rpm': 300,            # Velocidad máxima
    'default_rpm': 60,         # Velocidad por defecto
    'min_angle': 0.1125,       # Resolución real (360°/(200*16))
    'max_angle': 360.0,
    'angle_step': 0.0001,      # Precisión para la UI
    'pins': {
        'dir': 19,    # GPIO19 → DIR
        'step': 23,   # GPIO23 → STEP
        'enable': 18  # GPIO18 → ENABLE (active-low)
    }
}