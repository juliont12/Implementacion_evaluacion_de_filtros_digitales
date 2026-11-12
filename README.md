# Diseño y análisis de filtros digitales en Python

Este proyecto implementa, visualiza y evalúa el desempeño de tres arquitecturas de procesamiento digital de señales (DSP): filtros pasa bajos, pasa bandas y pasa altos, combinando enfoques **IIR** (Respuesta Infinita al Impulso) y **FIR** (Respuesta Finita al Impulso).

## Fundamentos teóricos aplicados

1. **Filtros IIR vs. FIR:**
    **IIR (Butterworth y Chebyshev):** Utilizan retroalimentación (polos y ceros). Logran transiciones con un orden computacional bajo, aunque presentan respuesta de fase no lineal.
    **FIR (Ventana Hamming):** Dependen únicamente de muestras pasadas y actuales de la entrada (solo ceros). Son intrínsecamente estables y poseen fase lineal exacta, pero requieren un mayor número de coeficientes para obtener pendientes pronunciadas.

2. **Aproximaciones de diseño:**
   **Butterworth:** Maximiza la planicidad en la banda de paso (sin rizado), ideal cuando se requiere preservar la amplitud exacta de la señal útil.
   **Chebyshev Tipo I:** Presenta una caída más pronunciada que Butterworth para el mismo orden, a cambio de introducir un rizado controlado en la banda de paso.
   **FIR con Ventana de Hamming:** Suaviza el truncamiento de la respuesta ideal al impulso, reduciendo los lóbulos secundarios en la banda de rechazo.

3. **Filtrado de fase cero:**
   * Aplica el filtro hacia adelante y luego en reversa sobre la señal. Esto duplica el orden efectivo de atenuación y cancela por completo el retardo de fase, permitiendo comparar punto a punto la señal filtrada con la señal pura de referencia.

## Requisitos 

El código requiere **Python 3.10+** y las bibliotecas científicas estándar:

## Configuración Experimental

Se sintetizó una señal de prueba muestreada compuesta por tres tonos sinusoidales más ruido blanco gaussiano:

| Tipo de Filtro | Arquitectura | Parámetros de Diseño | Frecuencia Objetivo | Componentes Suprimidas |
| :--- | :--- | :--- | :--- | :--- |
| **Pasa Bajos** | IIR Butterworth | Orden $4$, $f_c = 30\text{ Hz}$ | $10\text{ Hz}$ ($A = 1.0$) | $80\text{ Hz}$, $250\text{ Hz}$ y ruido alto |
| **Pasa Bandas** | IIR Chebyshev I | Orden $4$, rizado $1\text{ dB}$, $[50, 120]\text{ Hz}$ | $80\text{ Hz}$ ($A = 0.8$) | $10\text{ Hz}$, $250\text{ Hz}$ y ruido fuera de banda |
| **Pasa Altos** | FIR Ventana Hamming | $101$ taps (Tipo I), $f_c = 180\text{ Hz}$ | $250\text{ Hz}$ ($A = 0.6$) | $10\text{ Hz}$, $80\text{ Hz}$ y ruido bajo |


## Interpretación de los Resultados

Al ejecutar el script se generan tres paneles de análisis y un reporte en consola:

1. **Señal de Entrada (1):** En el dominio del tiempo, el ruido blanco y la superposición de frecuencias ocultan la forma de onda individual. Al aplicar la Transformada Rápida de Fourier (FFT), emergen claramente tres picos espectrales en $10\text{ Hz}$, $80\text{ Hz}$ y $250\text{ Hz}$ sobre un piso de ruido distribuido en todo el espectro.
2. **Respuesta en Frecuencia (2):** Muestra la ganancia en decibelios ($\text{dB}$) de cada filtro. Se observa el cruce por $-3\text{ dB}$ en las frecuencias de corte diseñadas, el ligero rizado en la banda de paso del Chebyshev y los lóbulos de atenuación característicos de la ventana de Hamming en la banda de rechazo.
3. **Evaluación Post-Filtrado y SNR (3):**
   * Cada filtro aísla su frecuencia objetivo eliminando los picos no deseados en el espectro FFT.
   * La **Relación Señal-Ruido (SNR)** incrementa sustancialmente después del filtrado (pasando de ~4 dB en la señal compuesta ruidosa a valores superiores a 14–18 dB por banda aislada). El ruido remanente visible en las ondas recuperadas corresponde exclusivamente a la fracción de energía del ruido blanco que cae dentro de la banda de paso de cada filtro.
