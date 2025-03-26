import socket
import network
import ujson
from config import WIFI_CONFIG, MOTOR_CONFIG
import gc
import time

class WebServer:
    def __init__(self, motor):
        self.motor = motor
        self.setup_wifi()
        self.socket = self._setup_socket()
        print("> Servidor HTTP listo")

    def setup_wifi(self):
        """Configura el Access Point WiFi"""
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(
            essid=WIFI_CONFIG['ap']['ssid'],
            password=WIFI_CONFIG['ap']['password'],
            authmode=WIFI_CONFIG['ap']['authmode'],
            channel=WIFI_CONFIG['ap']['channel']
        )
        
        # Esperar activación con timeout
        start_time = time.time()
        while not ap.active():
            if time.time() - start_time > WIFI_CONFIG['ap']['timeout']:
                raise RuntimeError("Timeout al activar el Access Point")
            time.sleep(0.5)
        
        print(f"> WiFi AP Configurado - IP: {ap.ifconfig()[0]}")

    def _setup_socket(self):
        """Configura el socket del servidor web"""
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 80))
        s.listen(1)
        return s

    def start(self):
        """Bucle principal del servidor"""
        while True:
            client = None
            try:
                client, addr = self.socket.accept()
                request = client.recv(1024).decode()
                
                if not request:
                    continue

                # Parsear solicitud HTTP
                first_line = request.split('\r\n')[0]
                method, path, _ = first_line.split()
                path = '/index.html' if path == '/' else path

                # Manejar rutas
                if path.startswith('/api'):
                    self._handle_api(client, path)
                else:
                    self._serve_static(client, path)
                
            except Exception as e:
                print(f"! Error en solicitud: {e}")
            finally:
                if client:
                    client.close()
                gc.collect()

    def _serve_static(self, client, path):
        """Sirve archivos estáticos (HTML, CSS, JS)"""
        try:
            # Seguridad: solo archivos en /static/
            filename = 'static/' + path.split('/')[-1]
            
            with open(filename, 'r') as f:
                content = f.read()
            
            # Determinar tipo MIME
            content_types = {
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg'
            }
            ext = filename[filename.rfind('.'):].lower()
            content_type = content_types.get(ext, 'text/plain')
            
            # Cabeceras HTTP con anti-caché
            headers = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                "Cache-Control: no-store, max-age=0\r\n"
                "Connection: close\r\n\r\n"
            )
            
            client.send(headers)
            client.send(content)
        except OSError:
            client.send("HTTP/1.1 404 Not Found\r\n\r\n")
        except Exception as e:
            print(f"! Error al servir archivo: {e}")
            client.send("HTTP/1.1 500 Internal Error\r\n\r\n")

    def _handle_api(self, client, path):
        """Maneja endpoints de la API"""
        response = {'status': 'error', 'message': 'Endpoint no válido'}
        
        try:
            if path == '/api/status':
                # Estado completo del motor
                response = {
                    'status': 'ok',
                    'data': self.motor.get_status()
                }
            
            elif path.startswith('/api/move?'):
                # Movimiento angular preciso
                params = self._parse_query(path)
                angle = float(params.get('angle', 0))
                rpm = float(params.get('rpm', self.motor.current_rpm))

                if not 1 <= rpm <= MOTOR_CONFIG['max_rpm']:
                    raise ValueError(f"RPM debe estar entre 1 y {MOTOR_CONFIG['max_rpm']}")
                
                actual_angle = self.motor.move_angle(angle, rpm)
                response = {
                    'status': 'ok',
                    'actual_angle': actual_angle,
                    'current_rpm': rpm
                }
            
            elif path.startswith('/api/divide?'):
                # División del círculo
                params = self._parse_query(path)
                divisions = int(params.get('divisions', 0))
                rpm = float(params.get('rpm', self.motor.current_rpm))
                
                if divisions < 2:
                    raise ValueError("Se requieren mínimo 2 divisiones")
                
                angle = self.motor.divide_circle(divisions, rpm)
                response = {
                    'status': 'ok',
                    'divisions': divisions,
                    'angle_per_division': angle,
                    'current_angle': self.motor.get_current_angle()
                }
            
            elif path == '/api/reset':
                # Reinicio a posición cero
                self.motor.reset_position()
                response = {
                    'status': 'ok',
                    'current_angle': 0.0
                }
            
            elif path == '/api/emergency_stop':
                # Parada de emergencia
                self.motor.emergency_stop()
                response = {
                    'status': 'ok',
                    'enabled': False
                }
            
            elif path == '/api/enable_motor':
                # Reactivar motor
                self.motor.enable_motor()
                response = {
                    'status': 'ok',
                    'enabled': True
                }
                
        except ValueError as e:
            response['message'] = f'Error en parámetros: {str(e)}'
        except Exception as e:
            response['message'] = f'Error interno: {str(e)}'
        
        # Enviar respuesta JSON
        client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        client.send(ujson.dumps(response))

    def _parse_query(self, path):
        """Extrae parámetros de consulta de la URL"""
        params = {}
        if '?' in path:
            query = path.split('?')[1].split(' ')[0]
            for pair in query.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key] = value
        return params