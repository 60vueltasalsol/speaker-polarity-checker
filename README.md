# 🔊 Verificador de Polaridad Acústica de Altavoces (Python)

Herramienta en Python para medir y comprobar la **polaridad acústica (fase absoluta)** de bocinas o monitores de estudio utilizando una interfaz de audio (como la **Behringer U-Phoria UMC22**) y un micrófono de medición omnidireccional (como el **Behringer ECM8000**).

---

## 📋 ¿Cómo funciona?

1. El script genera un pulso asimétrico suave (medio seno de 2 ms) para mover el diafragma del altavoz hacia afuera sin forzar componentes de alta frecuencia.
2. Graba la respuesta directa recibida por el micrófono de medición en tiempo real.
3. Analiza el **frente de onda directo** (la primera excursión antes del rebote mecánico/acústico) para determinar si la bocina comprime o descomprime el aire inicialmente:
   - **Polaridad Positiva (+):** El cono empuja hacia afuera primero (gráfico sube).
   - **Polaridad Invertida (-):** El cono se retrae hacia adentro primero (gráfico baja).

---

## 🛠 Requisitos de Hardware

- **Interfaz de audio:** Behringer UMC22 o similar con alimentación Phantom (+48V).
- **Micrófono:** Behringer ECM8000 u otro micrófono de medición calibrado.
- **Posicionamiento:** Colocar el micrófono a **5–15 cm** del centro del cono (campo cercano) para reducir el impacto de las reflexiones acústicas de la sala.

---

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/60vueltasalsol/speaker-polarity-checker.git
   cd speaker-polarity-checker