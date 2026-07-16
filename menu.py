"""
menu.py
Menú visual de adaptIA con orbe animado tipo Jarvis.
Se ejecuta en segundo plano mientras adaptIA escucha.
Muestra el estado del sistema, animación de voz y logs en tiempo real.
"""

import tkinter as tk
import math
import threading
import time
import queue
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

COLOR_BG = "#000000"
COLOR_ORB_BASE = "#1a0a00"
COLOR_ORB_RING1 = "#ff6600"
COLOR_ORB_RING2 = "#ff9900"
COLOR_ORB_RING3 = "#ffcc00"
COLOR_ORB_GLOW = "#ff4400"
COLOR_TEXT = "#ff8800"
COLOR_TEXT_DIM = "#663300"
COLOR_GREEN = "#00ff88"
COLOR_LOG = "#ff6600"
FONT_MAIN = ("Courier New", 11)
FONT_TITLE = ("Courier New", 18, "bold")
FONT_STATUS = ("Courier New", 10)

log_queue = queue.Queue()
estado_actual = {"texto": "ESCUCHA PASIVA", "color": COLOR_TEXT_DIM, "activo": False}


def agregar_log(mensaje):
    """Agrega un mensaje al log del menú."""
    log_queue.put(mensaje)


class MenuAdaptIA:
    def __init__(self, root):
        self.root = root
        self.root.title("adaptIA — Sistema activo")
        self.root.configure(bg=COLOR_BG)
        self.root.geometry("520x700")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", False)

        self.angulo = 0
        self.pulso = 0
        self.ondas = []
        self.logs = []
        self.MAX_LOGS = 8

        self._construir_ui()
        self._iniciar_animacion()
        self._procesar_logs()

    def _construir_ui(self):
        # Título
        tk.Label(
            self.root, text="◈ ORION — adaptIA ◈",
            font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_ORB_RING2
        ).pack(pady=(18, 0))

        tk.Label(
            self.root, text="Sistema de IA por voz activo",
            font=FONT_STATUS, bg=COLOR_BG, fg=COLOR_TEXT_DIM
        ).pack(pady=(2, 8))

        # Canvas para el orbe
        self.canvas = tk.Canvas(
            self.root, width=320, height=320,
            bg=COLOR_BG, highlightthickness=0
        )
        self.canvas.pack(pady=4)

        # Estado
        self.lbl_estado = tk.Label(
            self.root, text="● ESCUCHA PASIVA",
            font=("Courier New", 13, "bold"), bg=COLOR_BG, fg=COLOR_TEXT_DIM
        )
        self.lbl_estado.pack(pady=(4, 2))

        tk.Label(
            self.root, text='Di  "Orion"  para activar',
            font=FONT_STATUS, bg=COLOR_BG, fg=COLOR_TEXT_DIM
        ).pack(pady=(0, 8))

        # Separador
        tk.Frame(self.root, bg=COLOR_ORB_RING1, height=1).pack(fill="x", padx=30)

        # Log de actividad
        tk.Label(
            self.root, text="LOG DE ACTIVIDAD",
            font=("Courier New", 9), bg=COLOR_BG, fg=COLOR_TEXT_DIM
        ).pack(pady=(6, 2))

        self.frame_logs = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_logs.pack(fill="x", padx=24)

        self.labels_log = []
        for _ in range(self.MAX_LOGS):
            lbl = tk.Label(
                self.frame_logs, text="",
                font=("Courier New", 9), bg=COLOR_BG,
                fg=COLOR_TEXT_DIM, anchor="w"
            )
            lbl.pack(fill="x")
            self.labels_log.append(lbl)

        # Botón cerrar
        tk.Button(
            self.root, text="✕  Cerrar adaptIA",
            font=FONT_STATUS, bg=COLOR_BG, fg=COLOR_TEXT_DIM,
            relief="flat", cursor="hand2",
            command=self._cerrar
        ).pack(pady=(10, 6))

    def _dibujar_orbe(self):
        c = self.canvas
        c.delete("all")
        cx, cy, r = 160, 160, 90

        # Glow exterior pulsante
        glow_r = r + 30 + int(math.sin(self.pulso) * 12)
        for i in range(6, 0, -1):
            alpha_hex = format(int(i * 8), '02x')
            c.create_oval(
                cx - glow_r - i*4, cy - glow_r - i*4,
                cx + glow_r + i*4, cy + glow_r + i*4,
                outline=f"#ff{format(int(40+i*10), '02x')}00",
                width=1
            )

        # Anillos orbitales giratorios
        for idx, (radio_rel, vel, color) in enumerate([
            (1.55, 1.0, COLOR_ORB_RING1),
            (1.85, -0.7, COLOR_ORB_RING2),
            (2.15, 0.5, COLOR_ORB_RING3),
        ]):
            radio = int(r * radio_rel)
            angulo_rad = math.radians(self.angulo * vel + idx * 40)
            # Elipse inclinada simulada con arco
            c.create_oval(
                cx - radio, cy - int(radio * 0.28),
                cx + radio, cy + int(radio * 0.28),
                outline=color, width=1
            )
            # Punto brillante en el anillo
            px = cx + int(radio * math.cos(angulo_rad))
            py = cy + int(radio * 0.28 * math.sin(angulo_rad))
            c.create_oval(px-4, py-4, px+4, py+4, fill=color, outline="")

        # Partículas orbitales
        for i in range(12):
            ang = math.radians(self.angulo * 0.8 + i * 30)
            dist = r * 1.1 + int(math.sin(self.pulso + i) * 8)
            px = cx + int(dist * math.cos(ang))
            py = cy + int(dist * 0.45 * math.sin(ang))
            sz = 2 if i % 3 == 0 else 1
            c.create_oval(px-sz, py-sz, px+sz, py+sz, fill=COLOR_ORB_RING2, outline="")

        # Núcleo del orbe
        for i in range(5, 0, -1):
            factor = i / 5.0
            radio_nuc = int(r * factor)
            # Interpolación de color naranja→negro
            rr = int(200 * factor)
            gg = int(80 * factor * factor)
            color_nuc = f"#{rr:02x}{gg:02x}00"
            c.create_oval(
                cx - radio_nuc, cy - radio_nuc,
                cx + radio_nuc, cy + radio_nuc,
                fill=color_nuc, outline=""
            )

        # Brillo central
        brillo = int(60 + math.sin(self.pulso * 2) * 30)
        c.create_oval(
            cx-25, cy-25, cx+25, cy+25,
            fill=f"#{brillo+80:02x}{brillo//3:02x}00", outline=""
        )
        c.create_oval(cx-10, cy-10, cx+10, cy+10, fill="#ffcc88", outline="")

        # Ondas de voz si está activo
        if estado_actual["activo"]:
            for i, onda in enumerate(self.ondas):
                radio_onda = onda["radio"]
                alpha = max(0, 1 - radio_onda / 140)
                if alpha > 0:
                    color_onda = f"#{int(255*alpha):02x}{int(100*alpha):02x}00"
                    c.create_oval(
                        cx - radio_onda, cy - radio_onda,
                        cx + radio_onda, cy + radio_onda,
                        outline=color_onda, width=2
                    )

        # Líneas de escaneo decorativas
        for i in range(4):
            y_line = cy - 70 + i * 35
            c.create_line(cx-85, y_line, cx+85, y_line,
                         fill="#331100", width=1)

    def _iniciar_animacion(self):
        def animar():
            self.angulo = (self.angulo + 2) % 360
            self.pulso += 0.08

            # Actualizar ondas de voz
            if estado_actual["activo"]:
                if len(self.ondas) < 4 and int(self.pulso * 10) % 8 == 0:
                    self.ondas.append({"radio": 95})
                nuevas = []
                for o in self.ondas:
                    o["radio"] += 3
                    if o["radio"] < 145:
                        nuevas.append(o)
                self.ondas = nuevas
            else:
                self.ondas = []

            self._dibujar_orbe()
            self.root.after(40, animar)

        animar()

    def _procesar_logs(self):
        """Revisa la cola de logs y actualiza la UI."""
        try:
            while True:
                msg = log_queue.get_nowait()
                self.logs.append(msg)
                if len(self.logs) > self.MAX_LOGS:
                    self.logs.pop(0)
                for i, lbl in enumerate(self.labels_log):
                    if i < len(self.logs):
                        lbl.config(
                            text=f"› {self.logs[i][:55]}",
                            fg=COLOR_LOG if i == len(self.logs)-1 else COLOR_TEXT_DIM
                        )
                    else:
                        lbl.config(text="")
        except queue.Empty:
            pass
        self.root.after(200, self._procesar_logs)

    def actualizar_estado(self, texto, activo=False):
        """Actualiza el texto de estado y si está escuchando activamente."""
        estado_actual["activo"] = activo
        color = COLOR_GREEN if activo else COLOR_TEXT_DIM
        self.lbl_estado.config(text=f"● {texto}", fg=color)

    def _cerrar(self):
        self.root.destroy()
        os._exit(0)


_menu_instance = None


def iniciar_menu():
    """Inicia el menú visual en el hilo principal de Tkinter."""
    global _menu_instance
    root = tk.Tk()
    _menu_instance = MenuAdaptIA(root)
    root.mainloop()


def actualizar_estado_menu(texto, activo=False):
    """Llamar desde main.py para actualizar el estado del menú."""
    if _menu_instance:
        _menu_instance.root.after(0, lambda: _menu_instance.actualizar_estado(texto, activo))


def log_menu(mensaje):
    """Envía un mensaje al log del menú."""
    log_queue.put(mensaje)
