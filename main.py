from motor import StepperMotor
from server import WebServer
from config import MOTOR_CONFIG
import network
import machine

def main():
    try:
        print("\n=== INICIALIZANDO TORNO DIVISOR CNC ===")
        
        # 1. Inicializar motor
        motor = StepperMotor()
        
        # 2. Configurar servidor web
        server = WebServer(motor)
        
        # 3. Mostrar información de conexión
        ap_ip = network.WLAN(network.AP_IF).ifconfig()[0]
        print(f"\n> Configuración completada:")
        print(f"• Dirección IP: http://{ap_ip}")
        print(f"• Resolución: {360/(200*16):.4f}° por micropaso")
        print(f"• Velocidad máxima: {MOTOR_CONFIG['max_rpm']} RPM")
        print(f"• Precisión mínima: {MOTOR_CONFIG['min_angle']}°")
        print("\n=== SISTEMA LISTO PARA OPERAR ===")
        
        # 4. Iniciar servidor (bucle infinito)
        server.start()
        
    except Exception as e:
        print(f"\n! ERROR CRÍTICO: {str(e)}")
        print("> Reiniciando el sistema...")
        machine.reset()

if __name__ == "__main__":
    main()