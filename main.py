"""
Diseño, análisis y aplicación de filtros digitales (FIR e IIR)
--------------------------------------------------------------
Implementación de filtros pasa bajos, pasa bandas
y pasa altos sobre una señal compuesta contaminada
con ruido blanco gaussiano.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import rfft, rfftfreq


def calcular_espectro(senal: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Calcula el espectro de magnitud unilateral mediante FFT."""
    n = len(senal)
    magnitudes = (2.0 / n) * np.abs(rfft(senal))
    frecuencias = rfftfreq(n, d=1.0 / fs)
    return frecuencias, magnitudes


def calcular_snr(senal_pura: np.ndarray, senal_evaluada: np.ndarray) -> float:
    """Calcula la relación señal-ruido (SNR) en decibelios (dB)."""
    potencia_senal = np.sum(senal_pura ** 2)
    potencia_ruido = np.sum((senal_pura - senal_evaluada) ** 2)
    return 10 * np.log10(potencia_senal / potencia_ruido)


# 1. Definición de la señal de entrada
fs = 1000.0          # Frecuencia de muestreo (Hz) -> Nyquist = 500 Hz
duracion = 1.0       # Duración de la señal (segundos)
t = np.arange(0, duracion, 1.0 / fs)

# Componentes frecuenciales puras
f_baja, amp_baja = 10.0, 1.0     # Componente de baja frecuencia (10 Hz)
f_media, amp_media = 80.0, 0.8   # Componente de frecuencia intermedia (80 Hz)
f_alta, amp_alta = 250.0, 0.6    # Componente de alta frecuencia (250 Hz)

s_baja = amp_baja * np.sin(2 * np.pi * f_baja * t)
s_media = amp_media * np.sin(2 * np.pi * f_media * t)
s_alta = amp_alta * np.sin(2 * np.pi * f_alta * t)

# Señal compuesta limpia
senal_limpia = s_baja + s_media + s_alta

# Adición de ruido blanco gaussiano (media = 0, desviación estándar = 0.5)
rng = np.random.default_rng(seed=42)
ruido_blanco = rng.normal(loc=0.0, scale=0.5, size=len(t))
senal_ruidosa = senal_limpia + ruido_blanco


# 2. Diseño de los filtros digitales
# Filtro Pasa Bajos: IIR Butterworth (Orden 4, fc = 30 Hz)
# Objetivo: Aislar la componente de 10 Hz y suprimir 80 Hz, 250 Hz y ruido alto.
fc_lp = 30.0
sos_lp = signal.butter(N=4, Wn=fc_lp, btype="lowpass", fs=fs, output="sos")

# Filtro Pasa Bandas: IIR Chebyshev Tipo I (Orden 4, rizado = 1 dB, [50, 120] Hz)
# Objetivo: Aislar la componente de 80 Hz rechazando tanto bajas como altas frecuencias.
fc_bp = [50.0, 120.0]
sos_bp = signal.cheby1(N=4, rp=1.0, Wn=fc_bp, btype="bandpass", fs=fs, output="sos")

# Filtro Pasa Altos: FIR con ventana Hamming (101 coeficientes, fc = 180 Hz)
# Objetivo: Aislar la componente de 250 Hz. Se usa numtaps impar (Tipo I) para
# evitar un cero forzado en la frecuencia de Nyquist.
fc_hp = 180.0
numtaps_hp = 101
b_hp = signal.firwin(
    numtaps=numtaps_hp,
    cutoff=fc_hp,
    window="hamming",
    pass_zero=False,
    fs=fs,
)


# 3. Aplicación de los filtros a la señal
# Se emplea filtrado bidireccional (fase cero) para preservar la alineación temporal
filtrada_lp = signal.sosfiltfilt(sos_lp, senal_ruidosa)
filtrada_bp = signal.sosfiltfilt(sos_bp, senal_ruidosa)
filtrada_hp = signal.filtfilt(b_hp, [1.0], senal_ruidosa)

# Evaluación cuantitativa mediante SNR (antes vs. después de filtrar)
print("=== Evaluación de efectividad (SNR) ===")
print(f"SNR inicial (señal compuesta con ruido): {calcular_snr(senal_limpia, senal_ruidosa):.2f} dB")
print(f"SNR Pasa Bajos  (objetivo 10 Hz):        {calcular_snr(s_baja, filtrada_lp):.2f} dB")
print(f"SNR Pasa Bandas (objetivo 80 Hz):        {calcular_snr(s_media, filtrada_bp):.2f} dB")
print(f"SNR Pasa Altos  (objetivo 250 Hz):       {calcular_snr(s_alta, filtrada_hp):.2f} dB")


# 4. Visualización de los resultados
plt.style.use("seaborn-v0_8-darkgrid")

# --- 1: Señal de entrada antes del filtrado (tiempo y frecuencia) ---
fig1, axes1 = plt.subplots(2, 1, figsize=(11, 7))
fig1.suptitle("1. Análisis de la señal de entrada (antes del filtrado)", fontsize=13, fontweight="bold")

# Zoom en los primeros 0.25 segundos para visualizar las oscilaciones
mascara_zoom = t <= 0.25
axes1[0].plot(t[mascara_zoom], senal_ruidosa[mascara_zoom], label="Señal con ruido blanco", color="#7f8c8d", alpha=0.8)
axes1[0].plot(t[mascara_zoom], senal_limpia[mascara_zoom], label="Señal compuesta pura (10 + 80 + 250 Hz)", color="#1f77b4", linewidth=1.8)
axes1[0].set_title("Dominio del tiempo (Primeros 250 ms)")
axes1[0].set_xlabel("Tiempo [s]")
axes1[0].set_ylabel("Amplitud")
axes1[0].legend(loc="upper right")

freqs_in, mag_in = calcular_espectro(senal_ruidosa, fs)
axes1[1].plot(freqs_in, mag_in, color="#d62728", linewidth=1.2)
axes1[1].set_title("Dominio de la frecuencia (Espectro FFT)")
axes1[1].set_xlabel("Frecuencia [Hz]")
axes1[1].set_ylabel("Magnitud")
axes1[1].set_xlim(0, 500)

plt.tight_layout()

# --- 2: Respuesta en frecuencia de los filtros diseñados ---
fig2, ax2 = plt.subplots(figsize=(11, 5))
fig2.suptitle("2. Respuesta en frecuencia de los filtros (Magnitud en dB)", fontsize=13, fontweight="bold")

w_lp, h_lp = signal.sosfreqz(sos_lp, worN=2048, fs=fs)
w_bp, h_bp = signal.sosfreqz(sos_bp, worN=2048, fs=fs)
w_hp, h_hp = signal.freqz(b_hp, worN=2048, fs=fs)

ax2.plot(w_lp, 20 * np.log10(np.maximum(np.abs(h_lp), 1e-10)), label="Pasa Bajos (Butterworth IIR, fc=30 Hz)", linewidth=2)
ax2.plot(w_bp, 20 * np.log10(np.maximum(np.abs(h_bp), 1e-10)), label="Pasa Bandas (Chebyshev I IIR, 50-120 Hz)", linewidth=2)
ax2.plot(w_hp, 20 * np.log10(np.maximum(np.abs(h_hp), 1e-10)), label="Pasa Altos (FIR Hamming, fc=180 Hz)", linewidth=2)

ax2.axhline(-3, color="black", linestyle="--", linewidth=1, label="Atenuación -3 dB (Frecuencia de corte)")
ax2.set_ylim(-80, 5)
ax2.set_xlim(0, 500)
ax2.set_xlabel("Frecuencia [Hz]")
ax2.set_ylabel("Ganancia [dB]")
ax2.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.18), 
    ncol=2,                       
    frameon=True,
    facecolor="white",
    framealpha=0.95,
)

plt.tight_layout()

# --- 3: Comparación después del filtrado (tiempo y frecuencia) ---
fig3, axes3 = plt.subplots(3, 2, figsize=(13, 10))
fig3.suptitle("3. Comparación de Señales Filtradas vs. Componentes Originales", fontsize=13, fontweight="bold")

configuraciones = [
    ("Pasa Bajos (Butterworth)", filtrada_lp, s_baja, 0.25, "#2ca02c"),
    ("Pasa Bandas (Chebyshev I)", filtrada_bp, s_media, 0.10, "#ff7f0e"),
    ("Pasa Altos (FIR Hamming)", filtrada_hp, s_alta, 0.05, "#9467bd"),
]

for fila, (titulo, s_filt, s_ref, t_zoom, color) in enumerate(configuraciones):
    idx = t <= t_zoom
    # Columna izquierda: Dominio del tiempo
    axes3[fila, 0].plot(t[idx], s_ref[idx], label="Componente pura esperada", color="black", linestyle="--", linewidth=1.3)
    axes3[fila, 0].plot(t[idx], s_filt[idx], label="Señal filtrada", color=color, linewidth=1.8)
    axes3[fila, 0].set_title(f"{titulo} - Tiempo")
    axes3[fila, 0].set_xlabel("Tiempo [s]")
    axes3[fila, 0].set_ylabel("Amplitud")
    axes3[fila, 0].legend(loc="upper right", fontsize=8)

    # Columna derecha: Dominio de la frecuencia
    f_filt, m_filt = calcular_espectro(s_filt, fs)
    axes3[fila, 1].plot(freqs_in, mag_in, label="Espectro entrada (con ruido)", color="#bdc3c7", alpha=0.8)
    axes3[fila, 1].plot(f_filt, m_filt, label="Espectro filtrado", color=color, linewidth=1.8)
    axes3[fila, 1].set_title(f"{titulo} - Espectro FFT")
    axes3[fila, 1].set_xlabel("Frecuencia [Hz]")
    axes3[fila, 1].set_ylabel("Magnitud")
    axes3[fila, 1].set_xlim(0, 500)
    axes3[fila, 1].legend(loc="upper right", fontsize=8)

plt.tight_layout()
plt.show()