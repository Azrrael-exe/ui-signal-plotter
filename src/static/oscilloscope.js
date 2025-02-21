document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const statusIndicator = document.getElementById('connection-status');
    const statusText = document.getElementById('status-text');
    const connectBtn = document.getElementById('connect-btn');
    const disconnectBtn = document.getElementById('disconnect-btn');
    const oscilloscopeCanvas = document.getElementById('oscilloscope');
    
    // Variables globales
    let socket = null;
    let oscilloscopeChart = null;
    let dataPoints = [];
    
    // Parámetros configurables
    const config = {
        maxDataPoints: 20, // Valor por defecto: 20 muestras
        yAxisMin: -5,
        yAxisMax: 5,
        autoScale: false
    };
    
    // Crear los botones de control adicionales
    const createControlButtons = () => {
        const cardActions = document.querySelector('.card-actions');
        
        // Contenedor para controles de sample
        const sampleControls = document.createElement('div');
        sampleControls.className = 'sample-controls';
        sampleControls.style.display = 'flex';
        sampleControls.style.alignItems = 'center';
        sampleControls.style.marginLeft = 'auto';
        
        // Botón para disminuir samples
        const decreaseBtn = document.createElement('button');
        decreaseBtn.id = 'decrease-samples';
        decreaseBtn.innerHTML = '−';
        decreaseBtn.title = 'Disminuir número de muestras';
        decreaseBtn.style.padding = '4px 8px';
        
        // Elemento para mostrar la cantidad actual
        const samplesDisplay = document.createElement('span');
        samplesDisplay.id = 'samples-count';
        samplesDisplay.textContent = config.maxDataPoints;
        samplesDisplay.style.margin = '0 8px';
        samplesDisplay.style.minWidth = '24px';
        samplesDisplay.style.textAlign = 'center';
        
        // Botón para aumentar samples
        const increaseBtn = document.createElement('button');
        increaseBtn.id = 'increase-samples';
        increaseBtn.innerHTML = '+';
        increaseBtn.title = 'Aumentar número de muestras';
        increaseBtn.style.padding = '4px 8px';
        
        // Separador
        const separator = document.createElement('span');
        separator.style.margin = '0 12px';
        separator.style.color = '#ddd';
        separator.textContent = '|';
        
        // Botón de autoscale
        const autoscaleBtn = document.createElement('button');
        autoscaleBtn.id = 'autoscale-btn';
        autoscaleBtn.textContent = 'Autoscale';
        autoscaleBtn.title = 'Ajustar escala automáticamente';
        
        // Agregar elementos al contenedor
        sampleControls.appendChild(decreaseBtn);
        sampleControls.appendChild(samplesDisplay);
        sampleControls.appendChild(increaseBtn);
        sampleControls.appendChild(separator);
        sampleControls.appendChild(autoscaleBtn);
        
        // Agregar el contenedor después de los botones existentes
        cardActions.appendChild(sampleControls);
        
        // Agregar event listeners
        decreaseBtn.addEventListener('click', () => {
            if (config.maxDataPoints > 5) {
                setMaxDataPoints(config.maxDataPoints - 5);
                samplesDisplay.textContent = config.maxDataPoints;
            }
        });
        
        increaseBtn.addEventListener('click', () => {
            setMaxDataPoints(config.maxDataPoints + 5);
            samplesDisplay.textContent = config.maxDataPoints;
        });
        
        autoscaleBtn.addEventListener('click', toggleAutoScale);
    };
    
    // Generar etiquetas para el eje X donde la más reciente es 0
    const generateLabels = (numPoints) => {
        return Array(numPoints).fill().map((_, i) => -(numPoints - 1 - i));
    };
    
    // Configuración inicial del gráfico
    const initChart = () => {
        const ctx = oscilloscopeCanvas.getContext('2d');
        
        // Crear arrays vacíos para los datos iniciales
        const initialData = Array(config.maxDataPoints).fill(null);
        
        // Generar etiquetas donde la última (más reciente) es 0
        const timeLabels = generateLabels(config.maxDataPoints);
        
        oscilloscopeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [{
                    label: 'Señal',
                    data: initialData,
                    borderColor: '#2196F3',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 0 // Para mejor rendimiento
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Muestras'
                        },
                        ticks: {
                            callback: function(value) {
                                return value === 0 ? '0' : value;
                            }
                        },
                        reverse: false // Ya no necesitamos invertir, nuestras etiquetas ya están ordenadas
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Amplitud'
                        },
                        min: config.yAxisMin,
                        max: config.yAxisMax,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            title: function(tooltipItems) {
                                const value = parseInt(tooltipItems[0].label);
                                return value === 0 ? 'Muestra actual' : `Muestra ${value}`;
                            },
                            label: function(context) {
                                return `Valor: ${context.raw !== null ? context.raw.toFixed(2) : 'N/A'}`;
                            }
                        }
                    }
                }
            }
        });
    };
    
    // Función para actualizar el gráfico con nuevos datos
    const updateChart = (newValue) => {
        // Añadir el nuevo valor al array de datos
        dataPoints.push(newValue);
        
        // Mantener solo los últimos maxDataPoints valores
        if (dataPoints.length > config.maxDataPoints) {
            dataPoints.shift();
        }
        
        // Actualizar el dataset del gráfico
        oscilloscopeChart.data.datasets[0].data = [...dataPoints];
        
        // Actualizar las etiquetas del eje X (para que 0 sea siempre la muestra más reciente)
        oscilloscopeChart.data.labels = generateLabels(dataPoints.length);
        
        // Si autoscale está activado, ajustar los límites del eje Y
        if (config.autoScale && dataPoints.length > 0) {
            applyAutoScale();
        }
        
        // Actualizar el gráfico
        oscilloscopeChart.update();
    };
    
    // Función para aplicar autoscale
    const applyAutoScale = () => {
        if (dataPoints.length === 0) return;
        
        // Encontrar el valor mínimo y máximo en los datos actuales
        let min = Math.min(...dataPoints);
        let max = Math.max(...dataPoints);
        
        // Añadir un 10% de margen
        const range = max - min;
        min = min - range * 0.1;
        max = max + range * 0.1;
        
        // Asegurar un rango mínimo
        if (max - min < 1) {
            const center = (max + min) / 2;
            min = center - 0.5;
            max = center + 0.5;
        }
        
        // Actualizar la configuración y el gráfico
        config.yAxisMin = min;
        config.yAxisMax = max;
        
        oscilloscopeChart.options.scales.y.min = min;
        oscilloscopeChart.options.scales.y.max = max;
    };
    
    // Función para alternar autoscale
    const toggleAutoScale = () => {
        config.autoScale = !config.autoScale;
        
        // Actualizar el estado visual del botón
        const autoscaleBtn = document.getElementById('autoscale-btn');
        if (config.autoScale) {
            autoscaleBtn.classList.add('active');
            autoscaleBtn.style.backgroundColor = '#e8f5e9';
            autoscaleBtn.style.borderColor = '#81c784';
            applyAutoScale(); // Aplicar inmediatamente
        } else {
            autoscaleBtn.classList.remove('active');
            autoscaleBtn.style.backgroundColor = '';
            autoscaleBtn.style.borderColor = '';
            
            // Volver a los valores predeterminados
            config.yAxisMin = -5;
            config.yAxisMax = 5;
            oscilloscopeChart.options.scales.y.min = -5;
            oscilloscopeChart.options.scales.y.max = 5;
            oscilloscopeChart.update();
        }
    };
    
    // Funciones para gestionar la conexión WebSocket
    const connectWebSocket = () => {
        // Crear nueva conexión WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        socket = new WebSocket(wsUrl);
        
        // Evento que se dispara cuando la conexión se establece
        socket.onopen = function(event) {
            console.log('Conexión establecida con el servidor WebSocket');
            updateConnectionStatus(true);
        };
        
        // Evento que se dispara cuando se recibe un mensaje
        socket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                // Verificar si el mensaje contiene un valor
                if (data.value !== undefined) {
                    updateChart(data.value);
                }
                
                // Verificar si el mensaje contiene un error
                if (data.error) {
                    console.error('Error del servidor:', data.error);
                }
            } catch (error) {
                console.error('Error al procesar mensaje:', error);
            }
        };
        
        // Evento que se dispara cuando se cierra la conexión
        socket.onclose = function(event) {
            console.log('Conexión cerrada con el servidor WebSocket');
            updateConnectionStatus(false);
        };
        
        // Evento que se dispara cuando ocurre un error
        socket.onerror = function(error) {
            console.error('Error en la conexión WebSocket:', error);
            updateConnectionStatus(false);
        };
    };
    
    // Función para actualizar el estado visual de la conexión
    const updateConnectionStatus = (connected) => {
        if (connected) {
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Conectado';
            connectBtn.disabled = true;
            disconnectBtn.disabled = false;
        } else {
            statusIndicator.classList.remove('connected');
            statusText.textContent = 'Desconectado';
            connectBtn.disabled = false;
            disconnectBtn.disabled = true;
            
            // Limpiar el socket si existe
            if (socket) {
                socket = null;
            }
        }
    };
    
    // Función para cerrar la conexión WebSocket
    const disconnectWebSocket = () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    };
    
    // Función para cambiar el número máximo de muestras
    const setMaxDataPoints = (newMax) => {
        if (newMax > 0) {
            config.maxDataPoints = newMax;
            
            // Ajustar los datos actuales si es necesario
            if (dataPoints.length > newMax) {
                dataPoints = dataPoints.slice(-newMax);
            }
            
            // Actualizar el gráfico sin recrearlo
            oscilloscopeChart.data.labels = generateLabels(dataPoints.length);
            oscilloscopeChart.update();
            
            // Actualizar el display
            document.getElementById('samples-count').textContent = newMax;
        }
    };
    
    // Inicializar el gráfico al cargar la página
    initChart();
    
    // Crear botones de control adicionales
    createControlButtons();
    
    // Event Listeners para los botones
    connectBtn.addEventListener('click', function() {
        connectWebSocket();
    });
    
    disconnectBtn.addEventListener('click', function() {
        disconnectWebSocket();
    });
    
    // Event Listener para reiniciar el gráfico
    document.querySelector('.nav-icons .icon:first-child').addEventListener('click', function() {
        dataPoints = [];
        oscilloscopeChart.data.datasets[0].data = Array(config.maxDataPoints).fill(null);
        oscilloscopeChart.data.labels = generateLabels(config.maxDataPoints);
        oscilloscopeChart.update();
    });
    
    // Exponer funciones para posible uso externo
    window.oscilloscopeConfig = {
        setMaxDataPoints: setMaxDataPoints,
        toggleAutoScale: toggleAutoScale
    };
    
    // Cerrar la conexión WebSocket cuando se cierre la ventana
    window.addEventListener('beforeunload', function() {
        disconnectWebSocket();
    });
}); 