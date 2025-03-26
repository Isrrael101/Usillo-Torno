from machine import Pin
import time
from config import MOTOR_CONFIG

class StepperMotor:
    def __init__(self):
        # Configuración de pines GPIO
        self.dir_pin = Pin(MOTOR_CONFIG['pins']['dir'], Pin.OUT)
        self.step_pin = Pin(MOTOR_CONFIG['pins']['step'], Pin.OUT)
        self.en_pin = Pin(MOTOR_CONFIG['pins']['enable'], Pin.OUT, value=0)  # Active-low
        
        # Variables de estado
        self.position_steps = 0
        self.microsteps = MOTOR_CONFIG['microsteps']
        self.current_rpm = MOTOR_CONFIG['default_rpm']
        self.enabled = True
        
        print(f"> Motor inicializado (Resolución: {self._get_angle_per_step():.4f}°)")

    def _get_angle_per_step(self):
        """Calcula la resolución angular por micropaso"""
        return 360 / (MOTOR_CONFIG['steps_per_rev'] * self.microsteps)

    def move_angle(self, degrees, rpm=None):
        """Mueve el motor un ángulo específico con precisión de micropasos"""
        if not self.enabled:
            raise ValueError("Motor deshabilitado (active en parada de emergencia)")
        
        if rpm:
            self.set_rpm(rpm)
        
        # Cálculo preciso de pasos
        steps = round(degrees / self._get_angle_per_step())
        actual_angle = steps * self._get_angle_per_step()
        
        self._move_steps(steps)
        return actual_angle  # Devuelve el ángulo real alcanzado

    def _move_steps(self, steps):
        """Control preciso de micropasos"""
        self.dir_pin.value(1 if steps > 0 else 0)
        delay = self._calculate_step_delay()
        
        # Generación de pulsos STEP
        for _ in range(abs(steps)):
            self.step_pin.value(1)
            time.sleep_us(2)  # Ancho del pulso
            self.step_pin.value(0)
            time.sleep_us(delay - 2)  # Delay entre pasos
        
        self.position_steps += steps

    def divide_circle(self, divisions, rpm=None):
        """Divide el círculo en N partes con precisión decimal"""
        if divisions < 2:
            raise ValueError("Se requieren mínimo 2 divisiones")
        
        angle = 360 / divisions
        actual_angle = self.move_angle(angle, rpm)
        return actual_angle  # Ángulo exacto utilizado

    def reset_position(self):
        """Vuelve a la posición cero (0°)"""
        self.move_angle(-self.get_current_angle())

    def emergency_stop(self):
        """Detención inmediata del motor"""
        self.en_pin.value(1)  # Active-high para desactivar
        self.enabled = False
        print("> PARADA DE EMERGENCIA ACTIVADA")

    def enable_motor(self):
        """Reactivar el motor después de emergencia"""
        self.en_pin.value(0)  # Active-low para activar
        self.enabled = True
        print("> Motor reactivado")

    def get_current_angle(self):
        """Devuelve el ángulo actual con máxima precisión"""
        steps_per_360 = MOTOR_CONFIG['steps_per_rev'] * self.microsteps
        return (self.position_steps % steps_per_360) * 360 / steps_per_360

    def set_rpm(self, rpm):
        """Ajusta la velocidad con validación estricta"""
        if not 1 <= rpm <= MOTOR_CONFIG['max_rpm']:
            raise ValueError(f"RPM debe estar entre 1 y {MOTOR_CONFIG['max_rpm']}")
        self.current_rpm = rpm
        print(f"> Velocidad ajustada a {rpm} RPM")  # Debug

    def _calculate_step_delay(self):
        """Calcula el delay entre pasos en microsegundos"""
        steps_per_rev = MOTOR_CONFIG['steps_per_rev'] * self.microsteps
        return int(60000000 / (steps_per_rev * self.current_rpm))  # 60,000,000 µs/min

    def get_status(self):
        """Estado completo del motor"""
        return {
            'current_angle': self.get_current_angle(),
            'rpm': self.current_rpm,
            'max_rpm': MOTOR_CONFIG['max_rpm'],
            'enabled': self.enabled,
            'resolution': self._get_angle_per_step(),
            'steps_per_rev': MOTOR_CONFIG['steps_per_rev'],
            'microsteps': self.microsteps
        }