import json
import re
import tkinter as tk
from tkinter import ttk, messagebox, font
from tkcalendar import DateEntry
from datetime import datetime, date

# regex para nombre: letras (incluye acentos) y espacios
NOMBRE_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$")

# email regex que ya tienes
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

class DesignApp:
    def __init__(self, root):
        self.root = root
        self._config_root()
        self._create_styles()
        self._create_header()
        self._create_form()
        self._create_buttons()
    
        # Lugar para guardar reservas en memoria (simulado, para futuras integraciones)
        self._reservas_simuladas = []
        # Cargar reservas previas desde archivo (si existe)
        self._cargar_reservas_json()

    def _config_root(self):
        self.root.title("🥅 Sistema de Reservas de Canchas")
        self.root.geometry("760x460")
        self.root.minsize(640, 420)
        # Background color (soft)
        self.bg_color = "#efefef"
        self.card_bg = "#ffffff"
        self.root.configure(bg=self.bg_color)

    def _create_styles(self):
        style = ttk.Style(self.root)
        # Use a known theme that supports customization
        try:
            style.theme_use("clam")
        except:
            pass

        # Fonts
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=10)
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.entry_font = font.Font(family="Segoe UI", size=10)

        # TTK styles
        style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        style.configure("Header.TLabel", background=self.bg_color, font=self.title_font)
        style.configure("Subtitle.TLabel", background=self.bg_color, font=self.subtitle_font, foreground="#555555")
        style.configure("FormLabel.TLabel", background=self.card_bg, font=self.label_font, foreground="#333333")
        style.configure("Accent.TButton", background="#2b9edb", foreground="white", font=self.entry_font, padding=8)
        style.map("Accent.TButton",
                  background=[("active", "#1f89bf"), ("disabled", "#bcdbe9")])
        style.configure("Outline.TButton", background="#f3f3f3", foreground="#333333", padding=8)
        style.configure("TCombobox", padding=6)
        style.configure("TEntry", padding=6)

    def _create_header(self):
        header = ttk.Frame(self.root, style="Card.TFrame", padding=(20, 14), relief="flat")
        header.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.92)

        left = ttk.Frame(header, style="Card.TFrame", width=400)
        left.pack(side="left", anchor="w")
        ttk.Label(left, text="🥅 Sistema de Reservas de Canchas", style="Header.TLabel").pack(anchor="w")

        # Small visual accent on the right
        accent = ttk.Frame(header, style="Card.TFrame")
        accent.pack(side="right", anchor="e")
        ttk.Label(accent, text="Hoy: " + DateEntry().get_date().strftime("%Y-%m-%d"),
                  font=self.subtitle_font, background=self.card_bg).pack()

    def _create_form(self):
        # Main card frame
        card = ttk.Frame(self.root, style="Card.TFrame", padding=20)
        card.place(relx=0.5, rely=0.175, anchor="n", relwidth=0.92, relheight=0.70)

        # Two columns: left for fields, right for calendar + availability
        left_col = ttk.Frame(card, style="Card.TFrame")
        left_col.pack(side="left", fill="both", expand=True, padx=(0,12))

        right_col = ttk.Frame(card, style="Card.TFrame", width=260)
        right_col.pack(side="right", fill="y")

        # Field helper to create label + entry with consistent look
        def field(parent, label_text, row_pad=(6,6)):
            lbl = ttk.Label(parent, text=label_text, style="FormLabel.TLabel")
            ent = ttk.Entry(parent, font=self.entry_font)
            lbl.pack(fill="x", pady=(row_pad[0],2))
            ent.pack(fill="x")
            return ent

        # Fields (left column)
        self.nombre_entry = field(left_col, "Nombre completo")
        self.documento_entry = field(left_col, "Documento")
        self.telefono_entry = field(left_col, "Teléfono")
        # --- NUEVO: campo de correo electrónico ---
        self.email_entry = field(left_col, "Correo electrónico")

        # Select cancha (OptionMenu styled as Combobox)
        ttk.Label(left_col, text="Cancha", style="FormLabel.TLabel").pack(anchor="w", pady=(10,2))
        self.cancha_var = tk.StringVar(value="Sintética")
        self.cancha_combo = ttk.Combobox(left_col, textvariable=self.cancha_var, state="readonly")
        self.cancha_combo['values'] = ["Sintética", "Vóley"]
        self.cancha_combo.pack(fill="x")

        # Date + hour on left column (compact)
        container = ttk.Frame(left_col, style="Card.TFrame")
        container.pack(fill="x", pady=(10,0))
        # Fecha
        sub = ttk.Frame(container, style="Card.TFrame")
        sub.pack(side="left", expand=True, fill="x")
        ttk.Label(sub, text="Fecha", style="FormLabel.TLabel").pack(anchor="w", pady=(0,2))
        self.fecha_picker = DateEntry(sub, width=14, borderwidth=1, date_pattern='yyyy-mm-dd', mindate=date.today())
        self.fecha_picker.pack(fill="x")

        # Hora
        sub2 = ttk.Frame(container, style="Card.TFrame")
        sub2.pack(side="left", padx=(12,0), fill="x")
        ttk.Label(sub2, text="Hora", style="FormLabel.TLabel").pack(anchor="w", pady=(0,2))
        self.hora_var = tk.StringVar()
        self.hora_combo = ttk.Combobox(sub2, textvariable=self.hora_var, state="readonly", width=8)
        self.hora_combo['values'] = [f"{h}:00" for h in range(10, 22)]  # Horarios de 10:00 a 21:00
        self.hora_combo.pack(fill="x")

        # Right column: calendar preview + notes / availability
        ttk.Label(right_col, text="Vista de Fecha", style="FormLabel.TLabel").pack(anchor="w")
        cal_frame = ttk.Frame(right_col, style="Card.TFrame", padding=8, relief="ridge")
        cal_frame.pack(fill="both", expand=True, pady=(4,8))
        # DateEntry large for preview (disabled to avoid accidental change)
        self.preview_date = DateEntry(cal_frame, width=16, borderwidth=1, date_pattern='yyyy-mm-dd')
        self.preview_date.pack(pady=(6,8))
        # Availability / small info text
        info = ("Selecciona la fecha y hora.\n"
                "Los horarios que aparecen en gris no están disponibles.")
        ttk.Label(cal_frame, text=info, wraplength=200, background=self.card_bg, foreground="#555555").pack()

    def _create_buttons(self):
        # Lower button bar
        bar = ttk.Frame(self.root, style="Card.TFrame")
        bar.place(relx=0.5, rely=0.88, anchor="n", relwidth=0.92)

        # Left group (primary actions)
        left = ttk.Frame(bar, style="Card.TFrame")
        left.pack(side="left", fill="x", expand=True)
        btn_res = ttk.Button(left, text="Reservar", style="Accent.TButton", command=self.reservar)
        btn_res.pack(side="left", padx=6, ipadx=8)

        btn_cancel = ttk.Button(left, text="Cancelar", style="Outline.TButton", command=self.cancelar)
        btn_cancel.pack(side="left", padx=6, ipadx=8)

        # Right group (secondary)
        right = ttk.Frame(bar, style="Card.TFrame")
        right.pack(side="right", fill="x")
        btn_ver = ttk.Button(right, text="Ver reservas", style="Outline.TButton", command=self.ver_reservas)
        btn_ver.pack(side="left", padx=6, ipadx=8)
        btn_disp = ttk.Button(right, text="Disponibilidad", style="Outline.TButton", command=self.ver_disponibilidad)
        btn_disp.pack(side="left", padx=6, ipadx=8)

        # Add a subtle hover effect for Accent buttons
        for btn in (btn_res, btn_cancel, btn_ver, btn_disp):
            btn.bind("<Enter>", lambda e, b=btn: b.state(['active']))
            btn.bind("<Leave>", lambda e, b=btn: b.state(['!active']))

    # --- Lógica simulada (sin cambios funcionales importantes) ---
    def reservar(self):
        nombre = self.nombre_entry.get().strip()
        doc = self.documento_entry.get().strip()
        tel = self.telefono_entry.get().strip()
        email = self.email_entry.get().strip()
        cancha = self.cancha_var.get()
        fecha_str = self.fecha_picker.get()   # 'yyyy-mm-dd'
        hora = self.hora_var.get()            # ejemplo: '10:00' o '15:00'

        # --- Validaciones básicas ---
        if not nombre:
            messagebox.showerror("Error", "Por favor ingresa el nombre.")
            return
        # Validar que el nombre contenga letras y espacios únicamente
        if not NOMBRE_REGEX.fullmatch(nombre):
            messagebox.showerror("Error", "El nombre solo puede contener letras y espacios.")
            return

        if not doc:
            messagebox.showerror("Error", "Por favor ingresa el documento.")
            return
        if not doc.isdigit():
            messagebox.showerror("Error", "El documento debe contener solo números.")
            return
        # (opcional) validar longitud mínima/máxima:
        # if not (6 <= len(doc) <= 12): ...

        if not tel:
            messagebox.showerror("Error", "Por favor ingresa el teléfono.")
            return
        # Permitir + y dígitos: quitar espacios y guiones y comprobar
        tel_normalizado = re.sub(r"[ \-()]", "", tel)
        if not re.fullmatch(r"\+?\d{6,15}", tel_normalizado):
            messagebox.showerror("Error", "Ingrese un teléfono válido (solo dígitos, opcional '+' al inicio).")
            return

        if not email:
            messagebox.showerror("Error", "Por favor ingresa el correo electrónico.")
            return
        if not EMAIL_REGEX.fullmatch(email):
            messagebox.showerror("Error", "Por favor ingresa un correo electrónico válido.")
            return

        if not fecha_str:
            messagebox.showerror("Error", "Por favor selecciona una fecha.")
            return
        # convertir fecha a objeto date y validar no pasada
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido.")
            return

        hoy = date.today()
        if fecha_obj < hoy:
            messagebox.showerror("Error", "La fecha seleccionada ya pasó. Elige una fecha futura o hoy.")
            return

        if not hora:
            messagebox.showerror("Error", "Por favor selecciona una hora.")
            return
        # validar hora formato 'HH:MM' y rango permitido (ej. 10 a 21)
        try:
            hora_obj = datetime.strptime(hora, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido.")
            return

        # comprobar rango (ajusta según tu configuración)
        if not (10 <= hora_obj.hour <= 21):
            messagebox.showerror("Error", "La hora debe estar entre 10:00 y 21:00.")
            return

        # --- Si todo OK: preparar reserva (simulado / listo para backend) ---
        reserva = {
            "nombre": nombre,
            "documento": doc,
            "telefono": tel_normalizado,
            "email": email,
            "cancha": cancha,
            "fecha": fecha_str,
            "hora": hora,
        }

        # Guardar en la lista simulada
        self._reservas_simuladas.append(reserva)
        messagebox.showinfo("Reserva exitosa", "¡Reserva realizada con éxito!")
    
        # Guardar reservas simuladas en un archivo JSON    
        self._guardar_reservas_json()
    
        
    def _guardar_reservas_json(self, path="reservas.json"):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._reservas_simuladas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("No se pudo guardar reservas:", e)
        
    def _cargar_reservas_json(self, path="reservas.json"):
        """
        Carga reservas desde un archivo JSON si existe.
        Valida que el contenido sea una lista de dicts con claves esperadas.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            # No hay archivo: no hay reservas previas, continuar silenciosamente
            return
        except Exception as e:
            # Error leyendo/parsing JSON: mostrar alerta pero no romper la app
            print("Error cargando reservas:", e)
            messagebox.showwarning("Aviso", f"No se pudo leer {path}. Se ignorarán reservas previas.")
            return

        # Validar estructura básica: lista de dicts con las claves mínimas
        if not isinstance(data, list):
            messagebox.showwarning("Aviso", f"Formato inválido en {path} (se esperaba una lista).")
            return

        valid_reservas = []
        expected_keys = {"nombre", "documento", "telefono", "email", "cancha", "fecha", "hora"}
        for item in data:
            if not isinstance(item, dict):
                continue
            # comprobar que las claves esperadas están presentes (puedes relajar esto)
            if not expected_keys.issubset(set(item.keys())):
                # omitir registros incompletos
                continue

            # (opcional) validar formato de fecha/hora mínimo
            try:
                # validación ligera de fecha/hora; no lanza error si formato es correcto
                datetime.strptime(item["fecha"], "%Y-%m-%d")
                datetime.strptime(item["hora"], "%H:%M")
            except Exception:
                # si falla, omitir este registro
                continue

            valid_reservas.append(item)

        # asignar las reservas válidas a la lista en memoria
        if valid_reservas:
            self._reservas_simuladas = valid_reservas
            # notificar (opcional)
            messagebox.showinfo("Reservas cargadas", f"Se cargaron {len(valid_reservas)} reserva(s) desde {path}.")
        else:
            # no se cargó ninguna reserva válida, mantener lista vacía
            return

    def cancelar(self):
        messagebox.showinfo("Cancelar", "Reserva cancelada (simulado)")

    def ver_reservas(self):
        if not self._reservas_simuladas:
            messagebox.showinfo("Reservas", "No hay reservas registradas (simulado).")
            return

        win = tk.Toplevel(self.root)
        win.title("Reservas registradas")
        win.geometry("700x350")
        win.transient(self.root)

        columns = ("#","Nombre", "Email", "Fecha", "Hora", "Cancha")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Definir encabezados
        for col in columns:
            tree.heading(col, text=col)
            if col == "#":
                tree.column(col, anchor="center", width=40, stretch=False)
            else:
                tree.column(col, anchor="center")

        # Insertar datos
        for i, r in enumerate(self._reservas_simuladas, start=1):
            tree.insert("", "end", values=(
                i,
                r["nombre"],
                r["email"],
                r["fecha"],
                r["hora"],
                r["cancha"]
            ))

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def ver_disponibilidad(self):
        messagebox.showinfo("Disponibilidad", "Mostrando disponibilidad (simulado)")

if __name__ == "__main__":
    root = tk.Tk()
    app = DesignApp(root)
    root.mainloop()