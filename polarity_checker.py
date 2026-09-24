import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import sys

# -------------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------------
SAMPLE_RATE = 48000    # Frecuencia de muestreo UMC22
DURATION = 0.5         # Duración en segundos
THRESHOLD_RATIO = 0.20 # Sensibilidad de detección de llegada directa

def listar_dispositivos():
    print("\n--- DISPOSITIVOS DE AUDIO DETECTADOS ---")
    print(sd.query_devices())
    print("----------------------------------------\n")

def generar_pulso_positivo(fs, duration):
    total_samples = int(fs * duration)
    signal = np.zeros(total_samples, dtype=np.float32)
    
    pulse_len = int(fs * 0.002) # Pulso de 2 ms
    t = np.linspace(0, np.pi, pulse_len)
    pulse = np.sin(t) * 0.6
    
    start_idx = int(fs * 0.05)  # 50 ms de silencio inicial
    signal[start_idx : start_idx + pulse_len] = pulse
    return signal

def analizar_polaridad(rec_signal, fs):
    # Eliminar componente DC
    rec_signal = rec_signal - np.mean(rec_signal)
    
    max_amp = np.max(np.abs(rec_signal))
    if max_amp < 0.01:
        return "ERROR", 0, "Señal muy baja. Sube la ganancia en la UMC22."
    
    norm = rec_signal / max_amp
    
    # Detectar el primer punto que cruza el umbral (frente de onda directo)
    indices = np.where(np.abs(norm) > THRESHOLD_RATIO)[0]
    if len(indices) == 0:
        return "ERROR", 0, "No se detectó el impacto."
    
    first_idx = indices[0]
    val_inicial = norm[first_idx]
    
    # La polaridad la define el signo del frente inicial, no el rebote
    if val_inicial > 0:
        return "POSITIVA (Correcta)", first_idx, val_inicial
    else:
        return "INVERTIDA (Negativa / En contrafase)", first_idx, val_inicial

def main():
    listar_dispositivos()
    print("Configuración inicial (solo se pregunta una vez):")
    dev_in = input("ID de entrada (Mic UMC22) [ENTER para defecto]: ").strip()
    dev_out = input("ID de salida (Altavoz UMC22) [ENTER para defecto]: ").strip()
    
    input_device = int(dev_in) if dev_in else None
    output_device = int(dev_out) if dev_out else None

    tx_signal = generar_pulso_positivo(SAMPLE_RATE, DURATION)

    # Modo interactivo para que la ventana se actualice sin cerrarse
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 4))
    
    medicion_num = 1

    try:
        while True:
            print(f"\n>>> [Medición #{medicion_num}] Enviando pulso...")
            
            try:
                grabacion = sd.playrec(
                    tx_signal, 
                    samplerate=SAMPLE_RATE, 
                    channels=1, 
                    input_mapping=[1], # Canal 1 XLR
                    device=(input_device, output_device),
                    dtype='float32'
                )
                sd.wait()
            except Exception as e:
                print(f"Error con el audio: {e}")
                break

            rx_signal = grabacion.flatten()
            resultado, idx_pico, detalle = analizar_polaridad(rx_signal, SAMPLE_RATE)
            
            # Mostrar resultado en consola
            color = "\033[92m" if "POSITIVA" in resultado else "\033[91m"
            reset = "\033[0m"
            print("=" * 50)
            print(f" RESULTADO: {color}{resultado}{reset}")
            print("=" * 50)

            # Actualizar gráfica
            ax.clear()
            t_ms = (np.arange(len(rx_signal)) / SAMPLE_RATE) * 1000
            ax.plot(t_ms, rx_signal, label="Señal Recibida (Mic)")
            
            if resultado != "ERROR":
                t_impacto = (idx_pico / SAMPLE_RATE) * 1000
                ax.set_xlim(max(0, t_impacto - 5), t_impacto + 15)
                ax.axhline(0, color='black', linestyle='--', alpha=0.5)
                ax.axvline(t_impacto, color='r', linestyle=':', label='Llegada Directa')
            
            ax.set_title(f"Medición #{medicion_num} - {resultado}")
            ax.set_xlabel("Tiempo (ms)")
            ax.set_ylabel("Amplitud")
            ax.grid(True)
            ax.legend(loc='upper right')
            
            plt.tight_layout()
            plt.draw()
            plt.pause(0.05) # Refrescar la ventana gráfica

            # Opciones del usuario
            opcion = input("\nPresiona [ENTER] para medir otra vez | [q] para salir: ").strip().lower()
            if opcion == 'q':
                print("Finalizando mediciones...")
                break
                
            medicion_num += 1

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    finally:
        plt.close('all')

if __name__ == "__main__":
    main()