"""
dron_simulation3d.py
=====================================================================
Simulación 3D y Telemetría Analítica de Renderizado y Física de un
Dron de Entregas mediante Cálculo Diferencial e Integral.

Trabajo Autónomo - Tercer Bimestre - Matemática Aplicada
Instituto Tecnológico Superior Cordillera

Modela, con VPython, la trayectoria de un dron cuya altitud sigue:
    h(t) = -0.1 t^4 + 1.6 t^3 - 7.2 t^2 + 10 t + 5      (0 <= t <= 10 s)

y despliega en tiempo real:
    - Altitud actual                h(t)
    - Velocidad vertical (derivada) h'(t)
    - Temperatura del Motor         T(t)
    - Datos acumulados (integral definida de D(t), calculada
      dinámicamente con la regla del trapecio como aproximación
      numérica del área bajo la curva)

Al finalizar la animación abre una figura de matplotlib con 3
subgráficas: posición, velocidad (con recta tangente en el máximo)
y transferencia de datos (con el área sombreada entre t=1 y t=4).
=====================================================================
"""

import numpy as np
from vpython import (canvas, box, sphere, curve, vector, color, rate,
                     label, arrow, wtext)
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# 1. MODELOS MATEMÁTICOS (Fases 1, 2 y 3 del documento analítico)
# ---------------------------------------------------------------------

# --- Fase 1: Altitud y Velocidad ---
def h(t):
    """Altitud del dron h(t) [m]."""
    return -0.1 * t**4 + 1.6 * t**3 - 7.2 * t**2 + 10 * t + 5

def v(t):
    """Velocidad vertical instantánea v(t) = h'(t) [m/s]."""
    return -0.4 * t**3 + 4.8 * t**2 - 14.4 * t + 10

def a(t):
    """Aceleración vertical h''(t) [m/s^2] (criterio de segunda derivada)."""
    return -1.2 * t**2 + 9.6 * t - 14.4

# --- Fase 2: Temperatura del Motor ---
def T_prime(t):
    """Tasa de calentamiento instantánea T'(t) [°C/s]"""
    return 0.6 * t**2 - 2 * t + 4

def T(t):
    """
    Antiderivada T(t) = integral(T'(t) dt).
    Sabiendo que T(0) = 22, la constante C = 22.
    T(t) = 0.2*t^3 - t^2 + 4t + 22
    """
    return 0.2 * t**3 - t**2 + 4 * t + 22

# --- Fase 3: Transferencia de Datos ---
def D(t):
    """Tasa de transferencia de datos de la cámara 4K D(t) [MB/s]."""
    return 3 * t**2 + 2 * t + 5

def F(t):
    """Antiderivada analítica de D(t): F(t) = t^3 + t^2 + 5t."""
    return t**3 + t**2 + 5 * t

# Trayectoria horizontal (x, z) del dron:
def x_of_t(t):
    return 2.0 * t - 10.0          # se desplaza en línea recta en x

def z_of_t(t):
    return 3.0 * np.sin(0.4 * t)   # leve oscilación lateral en z


# ---------------------------------------------------------------------
# 2. CONFIGURACIÓN DE LA ESCENA 3D
# ---------------------------------------------------------------------

scene = canvas(title="Simulación 3D - Telemetría de Dron (Cálculo Diferencial e Integral)",
                width=1000, height=600, background=vector(0.85, 0.9, 0.97))

# Suelo de referencia
ground = box(pos=vector(0, -0.05, 0), size=vector(60, 0.1, 30),
             color=vector(0.55, 0.75, 0.55))

# Cuerpo del dron
body = box(pos=vector(x_of_t(0), h(0), z_of_t(0)),
           size=vector(1.4, 0.35, 1.4), color=color.red)

rotor_offsets = [vector(0.9, 0.15, 0.9), vector(-0.9, 0.15, 0.9),
                 vector(0.9, 0.15, -0.9), vector(-0.9, 0.15, -0.9)]
rotors = [sphere(pos=body.pos + off, radius=0.18, color=color.black)
          for off in rotor_offsets]

# Estela de la trayectoria (curva 3D)
trail = curve(color=color.blue, radius=0.03)

# Vector de velocidad vertical (flecha) para visualizar h'(t)
vel_arrow = arrow(pos=body.pos, axis=vector(0, 0, 0), shaftwidth=0.08,
                   color=color.orange)

# HUD de telemetría (texto 2D superpuesto)
hud = wtext(text="Iniciando simulación...\n")

# ---------------------------------------------------------------------
# 3. BUCLE DE SIMULACIÓN (0 a 10 s)
# ---------------------------------------------------------------------

dt = 0.02          # paso de tiempo de la animación [s]
t = 0.0
t_max = 10.0

datos_acumulados = 0.0   # integral definida de D(t) acumulada dinámicamente
t_prev = 0.0
D_prev = D(0.0)

while t <= t_max:
    rate(60)

    # --- posición 3D según h(t) y trayectoria horizontal ---
    pos_actual = vector(x_of_t(t), h(t), z_of_t(t))
    body.pos = pos_actual
    for rotor, off in zip(rotors, rotor_offsets):
        rotor.pos = pos_actual + off
    trail.append(pos=pos_actual)

    # --- vector de velocidad vertical (derivada) ---
    vel_arrow.pos = pos_actual
    vel_arrow.axis = vector(0, v(t) * 0.15, 0)   # escalado visual
    vel_arrow.color = color.orange if v(t) >= 0 else color.red

    # --- acumulación dinámica de datos: Integral Definida ---
    D_actual = D(t)
    datos_acumulados += (D_prev + D_actual) / 2.0 * dt
    D_prev = D_actual

    # --- HUD de telemetría en tiempo real ---
    hud.text = (
        f"t = {t:5.2f} s\n"
        f"Altitud h(t)         = {h(t):7.2f} m\n"
        f"Velocidad h'(t)      = {v(t):7.2f} m/s\n"
        f"Aceleración h''(t)   = {a(t):7.2f} m/s^2\n"
        f"Temp. Motor T(t)     = {T(t):7.2f} °C\n"
        f"Datos D(t)           = {D_actual:7.2f} MB/s\n"
        f"Datos acumulados     = {datos_acumulados:7.2f} MB "
        f"(∫D(t)dt, Teorema Fundamental del Cálculo)\n"
    )

    t += dt

hud.text += "\n--- Simulación finalizada (t = 10 s) ---\n"
print("\n" + "="*50)
print("  RESULTADOS ANALÍTICOS PARA EL REPORTE PDF")
print("="*50)
print(f"FASE 1: Velocidad en t=2s es h'(2) = {v(2):.2f} m/s")
print(f"FASE 1: Velocidad en t=6s es h'(6) = {v(6):.2f} m/s")
print(f"FASE 2: Ecuación de T(t) = 0.2t^3 - t^2 + 4t + 22 (C=22)")
print(f"FASE 3: Integral Analítica ∫[1,4] D(t)dt = {F(4)-F(1):.2f} MB")
print("="*50 + "\n")
print("Abriendo gráficas de resumen (matplotlib)...")

# ---------------------------------------------------------------------
# 4. GRÁFICA DE RESUMEN (3 SUBPLOTS)
# ---------------------------------------------------------------------

t_arr = np.linspace(0, 10, 500)
h_arr = h(t_arr)
v_arr = v(t_arr)
D_arr = D(t_arr)

fig, axs = plt.subplots(3, 1, figsize=(9, 11))

# --- Subplot 1: Posición / Altitud h(t) ---
axs[0].plot(t_arr, h_arr, color="royalblue", linewidth=2, label="h(t)")
axs[0].axhline(0, color="gray", linewidth=0.7)
axs[0].set_title("Gráfica 1: Posición / Altitud h(t)")
axs[0].set_xlabel("t (s)")
axs[0].set_ylabel("Altitud (m)")
axs[0].grid(alpha=0.3)
axs[0].legend()

# --- Subplot 2: Velocidad v(t) = h'(t) con recta tangente en el máximo ---
t_star = 6.0
v_star = v(t_star)
a_star = a(t_star)

tangente = v_star + a_star * (t_arr - t_star)

axs[1].plot(t_arr, v_arr, color="darkorange", linewidth=2, label="v(t) = h'(t)")
axs[1].plot(t_arr, tangente, "--", color="crimson", linewidth=1.3,
            label=f"Tangente en t={t_star:.2f}s")
axs[1].scatter([t_star], [v_star], color="crimson", zorder=5)
axs[1].axhline(0, color="gray", linewidth=0.7)
axs[1].set_title("Gráfica 2: Velocidad v(t) = h'(t) con recta tangente")
axs[1].set_xlabel("t (s)")
axs[1].set_ylabel("Velocidad (m/s)")
axs[1].set_ylim(min(v_arr) - 5, max(v_arr) + 5)
axs[1].grid(alpha=0.3)
axs[1].legend()

# --- Subplot 3: Transferencia de datos D(t) con área sombreada [1,4] ---
axs[2].plot(t_arr, D_arr, color="seagreen", linewidth=2, label="D(t)")
mask = (t_arr >= 1) & (t_arr <= 4)
axs[2].fill_between(t_arr[mask], D_arr[mask], color="seagreen", alpha=0.35,
                     label=f"Área = ∫[1,4] D(t)dt = {F(4)-F(1):.0f} MB")
axs[2].axvline(1, color="gray", linestyle=":", linewidth=1)
axs[2].axvline(4, color="gray", linestyle=":", linewidth=1)
axs[2].set_title("Gráfica 3: Transferencia de datos D(t) — Integral Definida")
axs[2].set_xlabel("t (s)")
axs[2].set_ylabel("D(t) (MB/s)")
axs[2].grid(alpha=0.3)
axs[2].legend()

plt.tight_layout()
plt.savefig("resumen_telemetria.png", dpi=150)
plt.show()