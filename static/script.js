class DivisorController {
    constructor() {
        // Configuración del motor
        this.config = {
            maxRpm: 300,
            minRpm: 1,
            resolution: 0.1125
        };

        // Elementos del DOM
        this.elements = {
            rpmSlider: document.getElementById('rpm-slider'),
            rpmInput: document.getElementById('rpm-input'),
            currentRpm: document.getElementById('current-rpm'),
            divisionsInput: document.getElementById('divisions'),
            preciseAngle: document.getElementById('precise-angle'),
            divideBtn: document.getElementById('divide-btn'),
            nextBtn: document.getElementById('next-btn'),
            preciseBtn: document.getElementById('precise-btn'),
            resetBtn: document.getElementById('reset-btn'),
            emergencyBtn: document.getElementById('emergency-btn'),
            enableBtn: document.getElementById('enable-btn'),
            currentAngle: document.getElementById('current-angle'),
            currentDivision: document.getElementById('current-division'),
            totalDivisions: document.getElementById('total-divisions'),
            anglePerDivision: document.getElementById('angle-per-division'),
            maxRpmDisplay: document.getElementById('max-rpm'),
            resolutionDisplay: document.getElementById('resolution'),
            resultDisplay: document.getElementById('operation-result'),
            angleDisplay: document.getElementById('angle-display'),
            connectionStatus: document.getElementById('connection-status')
        };

        // Estado del sistema
        this.currentDivision = 0;
        this.totalDivisions = 0;
        this.anglePerDivision = 0;

        this.init();
    }

    init() {
        // Configurar valores iniciales
        this.elements.maxRpmDisplay.textContent = this.config.maxRpm;
        this.elements.resolutionDisplay.textContent = this.config.resolution;

        // Configurar event listeners
        this.setupEventListeners();
        
        // Iniciar actualización de estado
        this.startStatusUpdates();
    }

    setupEventListeners() {
        // Control de velocidad
        this.elements.rpmSlider.addEventListener('input', (e) => {
            const rpm = parseInt(e.target.value);
            this.elements.rpmInput.value = rpm;
            this.updateRpm(rpm);
        });

        this.elements.rpmInput.addEventListener('change', (e) => {
            let rpm = parseInt(e.target.value) || this.config.minRpm;
            rpm = Math.max(this.config.minRpm, Math.min(this.config.maxRpm, rpm));
            this.elements.rpmInput.value = rpm;
            this.elements.rpmSlider.value = rpm;
            this.updateRpm(rpm);
        });

        // Botones de control
        this.elements.divideBtn.addEventListener('click', () => this.handleDivide());
        this.elements.nextBtn.addEventListener('click', () => this.handleNextDivision());
        this.elements.preciseBtn.addEventListener('click', () => this.handlePreciseMove());
        this.elements.resetBtn.addEventListener('click', () => this.handleReset());
        this.elements.emergencyBtn.addEventListener('click', () => this.handleEmergencyStop());
        this.elements.enableBtn.addEventListener('click', () => this.handleEnableMotor());
    }

    async updateRpm(rpm) {
        try {
            const response = await this.fetchAPI('/move', {
                angle: 0,  // Movimiento de 0 grados solo para cambiar RPM
                rpm: rpm
            });
            
            if (response.status === 'ok') {
                this.elements.currentRpm.textContent = rpm;
                this.showResult(`Velocidad ajustada a ${rpm} RPM`, 'success');
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async fetchAPI(endpoint, params = {}) {
        try {
            let url = `/api${endpoint}`;
            if (Object.keys(params).length > 0) {
                url += `?${new URLSearchParams(params)}`;
            }
            
            const response = await fetch(url, {
                cache: 'no-store',
                headers: { 'Cache-Control': 'no-cache' }
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
            
        } catch (error) {
            console.error("Error en la API:", error);
            this.showResult("Error de conexión", 'error');
            throw error;
        }
    }

    async handleDivide() {
        try {
            const divisions = parseInt(this.elements.divisionsInput.value);
            const rpm = parseInt(this.elements.rpmInput.value);
            
            if (divisions < 2) {
                throw new Error("Mínimo 2 divisiones");
            }
            
            const response = await this.fetchAPI('/divide', { divisions, rpm });
            
            if (response.status === 'ok') {
                this.totalDivisions = divisions;
                this.currentDivision = 1;
                this.anglePerDivision = response.angle_per_division;
                
                this.updateUI();
                this.showResult(
                    `Círculo dividido en ${divisions} partes de ${response.angle_per_division.toFixed(4)}°`,
                    'success'
                );
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async handleNextDivision() {
        try {
            if (this.totalDivisions === 0) {
                throw new Error("Primero divida el círculo");
            }
            
            const response = await this.fetchAPI('/move', {
                angle: this.anglePerDivision,
                rpm: parseInt(this.elements.rpmInput.value)
            });
            
            if (response.status === 'ok') {
                this.currentDivision = (this.currentDivision % this.totalDivisions) + 1;
                this.updateUI();
                this.showResult(
                    `División ${this.currentDivision}/${this.totalDivisions} completada`,
                    'success'
                );
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async handlePreciseMove() {
        try {
            const angle = parseFloat(this.elements.preciseAngle.value);
            if (isNaN(angle)) {
                throw new Error("Ingrese un ángulo válido");
            }
            
            const rpm = parseInt(this.elements.rpmInput.value);
            const response = await this.fetchAPI('/move', { angle, rpm });
            
            if (response.status === 'ok') {
                this.showResult(
                    `Movido a ${response.actual_angle.toFixed(4)}°`,
                    'success'
                );
                this.elements.preciseAngle.value = '';
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async handleReset() {
        try {
            const response = await this.fetchAPI('/reset');
            if (response.status === 'ok') {
                this.currentDivision = 0;
                this.updateUI();
                this.showResult("Posición reiniciada a 0°", 'success');
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async handleEmergencyStop() {
        try {
            const response = await this.fetchAPI('/emergency_stop');
            if (response.status === 'ok') {
                this.showResult("¡PARADA DE EMERGENCIA ACTIVADA!", 'error');
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async handleEnableMotor() {
        try {
            const response = await this.fetchAPI('/enable_motor');
            if (response.status === 'ok') {
                this.showResult("Motor reactivado", 'success');
            }
        } catch (error) {
            this.showResult(`Error: ${error.message}`, 'error');
        }
    }

    async updateStatus() {
        try {
            const response = await this.fetchAPI('/status');
            if (response.status === 'ok') {
                const data = response.data;
                
                // Actualizar displays
                this.elements.currentAngle.textContent = data.current_angle.toFixed(4);
                this.elements.rpmInput.value = data.rpm;
                this.elements.rpmSlider.value = data.rpm;
                this.elements.currentRpm.textContent = data.rpm;
                
                // Actualizar visualización
                this.elements.angleDisplay.style.background = `
                    conic-gradient(
                        var(--secondary) 0deg,
                        var(--secondary) ${data.current_angle}deg,
                        transparent ${data.current_angle}deg 360deg
                    )`;
                
                // Estado de conexión
                this.updateConnectionStatus(true);
                
                // Estado de botones
                this.elements.enableBtn.disabled = data.enabled;
                this.elements.emergencyBtn.disabled = !data.enabled;
            }
        } catch (error) {
            console.error("Error al actualizar estado:", error);
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected) {
        const status = this.elements.connectionStatus;
        if (connected) {
            status.textContent = '● Conectado';
            status.style.color = 'var(--success)';
        } else {
            status.textContent = '● Desconectado';
            status.style.color = 'var(--danger)';
        }
    }

    updateUI() {
        this.elements.currentDivision.textContent = this.currentDivision;
        this.elements.totalDivisions.textContent = this.totalDivisions;
        this.elements.anglePerDivision.textContent = this.anglePerDivision.toFixed(4);
    }

    showResult(message, type = 'info') {
        const element = this.elements.resultDisplay;
        element.textContent = message;
        element.className = 'result ' + type;
    }

    startStatusUpdates() {
        this.updateStatus();
        setInterval(() => this.updateStatus(), 1000);
    }
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new DivisorController();
});