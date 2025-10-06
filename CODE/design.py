import json
import re
import tkinter as tk
from tkinter import ttk, messagebox, font
from tkcalendar import DateEntry
from datetime import datetime, date

NOMBRE_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$")
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

class DesignApp:
    def __init__(self, root):
        self.root = root
        self._config_root()
        self._create_styles()
        self._create_header()
        self._create_form()
        self._create_buttons()
    
        self._reservas_simuladas = []
        self._cargar_reservas_json()

    def _config_root(self):
        self.root.title("🥅 Sistema de Reservas de Canchas")
        self.root.geometry("760x460")
        self.root.minsize(640, 420)
        self.bg_color = "#efefef"
        self.card_bg = "#ffffff"
        self.root.configure(bg=self.bg_color)

    def _create_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except:
            pass

        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=10)
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.entry_font = font.Font(family="Segoe UI", size=10)

        style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        style.configure("Header.TLabel", background=self.bg_color, font=self.title_font)
        style.configure("FormLabel.TLabel", background=self.card_bg, font=self.label_font)
        style.configure("Accent.TButton", background="#2b9edb", foreground="white", font=self.entry_font, padding=8)
        style.map("Accent.TButton", background=[("active", "#1f89bf")])
        style.configure("Outline.TButton", background="#f3f3f3", foreground="#333333", padding=8)

    def _create_header(self):
        header = ttk.Frame(self.root, style="Card.TFrame", padding=(20, 14))
        header.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.92)
        ttk.Label(header, text="🥅 Sistema de Reservas de Canchas", style="Header.TLabel").pack(anchor="w")

    def _create_form(self):
        card = ttk.Frame(self.root, style="Card.TFrame", padding=20)
        card.place(relx=0.5, rely=0.175, anchor="n", relwidth=0.92, relheight=0.70)

        left_col = ttk.Frame(card, style="Card.TFrame")
        left_col.pack(side="left", fill="both", expand=True, padx=(0,12))

        def field(parent, label_text):
            ttk.Label(parent, text=label_text, style="FormLabel.TLabel").pack(anchor="w", pady=(6,2))
            ent = ttk.Entry(parent, font=self.entry_font)
            ent.pack(fill="x")
            return ent

        self.nombre_entry = field(left_col, "Nombre completo")
        self.documento_entry = field(left_col, "Documento")
        self.telefono_entry = field(left_col, "Teléfono")
        self.email_entry = field(left_col, "Correo electrónico")

        ttk.Label(left_col, text="Cancha", style="FormLabel.TLabel").pack(anchor="w", pady=(10,2))
        self.cancha_var = tk.StringVar(value="Sintética")
        self.cancha_combo = ttk.Combobox(left_col, textvariable=self.cancha_var, state="readonly")
        self.cancha_combo['values'] = ["Sintética", "Vóley"]
        self.cancha_combo.pack(fill="x")

        container = ttk.Frame(left_col, style="Card.TFrame")
        container.pack(fill="x", pady=(10,0))

        ttk.Label(container, text="Fecha", style="FormLabel.TLabel").grid(row=0, column=0, sticky="w")
        self.fecha_picker = DateEntry(container, width=14, borderwidth=1, date_pattern='yyyy-mm-dd', mindate=date.today())
        self.fecha_picker.grid(row=1, column=0, padx=4)

        ttk.Label(container, text="Hora", style="FormLabel.TLabel").grid(row=0, column=1, sticky="w")
        self.hora_var = tk.StringVar()
        self.hora_combo = ttk.Combobox(container, textvariable=self.hora_var, state="readonly", width=8)
        self.hora_combo['values'] = [f"{h}:00" for h in range(10, 22)]
        self.hora_combo.grid(row=1, column=1, padx=4)

    def _create_buttons(self):
        bar = ttk.Frame(self.root, style="Card.TFrame")
        bar.place(relx=0.5, rely=0.88, anchor="n", relwidth=0.92)

        left = ttk.Frame(bar, style="Card.TFrame")
        left.pack(side="left", fill="x", expand=True)
        ttk.Button(left, text="Reservar", style="Accent.TButton", command=self.reservar).pack(side="left", padx=6, ipadx=8)

        right = ttk.Frame(bar, style="Card.TFrame")
        right.pack(side="right", fill="x")
        ttk.Button(right, text="Ver reservas", style="Outline.TButton", command=self.ver_reservas).pack(side="left", padx=6)
        ttk.Button(right, text="Disponibilidad", style="Outline.TButton", command=self.ver_disponibilidad).pack(side="left", padx=6)

    # ---- Funciones principales ----
    def reservar(self):
        nombre = self.nombre_entry.get().strip()
        doc = self.documento_entry.get().strip()
        tel = self.telefono_entry.get().strip()
        email = self.email_entry.get().strip()
        cancha = self.cancha_var.get()
        fecha_str = self.fecha_picker.get()
        hora = self.hora_var.get()

        if not NOMBRE_REGEX.fullmatch(nombre or ""):
            return messagebox.showerror("Error", "El nombre solo puede contener letras y espacios.")
        if not doc.isdigit():
            return messagebox.showerror("Error", "El documento debe contener solo números.")
        if not re.fullmatch(r"\+?\d{6,15}", re.sub(r"[ \-()]", "", tel or "")):
            return messagebox.showerror("Error", "Teléfono inválido.")
        if not EMAIL_REGEX.fullmatch(email or ""):
            return messagebox.showerror("Error", "Correo electrónico inválido.")

        reserva = {
            "nombre": nombre, "documento": doc, "telefono": tel,
            "email": email, "cancha": cancha, "fecha": fecha_str, "hora": hora,
        }

        self._reservas_simuladas.append(reserva)
        self._guardar_reservas_json()
        messagebox.showinfo("Reserva exitosa", "¡Reserva realizada con éxito!")

    def _guardar_reservas_json(self, path="reservas.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._reservas_simuladas, f, ensure_ascii=False, indent=2)

    def _cargar_reservas_json(self, path="reservas.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._reservas_simuladas = json.load(f)
        except FileNotFoundError:
            self._reservas_simuladas = []

    # --- NUEVO: Ventana de ver reservas con botones editar / cancelar ---
    def ver_reservas(self):
        if not self._reservas_simuladas:
            return messagebox.showinfo("Reservas", "No hay reservas registradas.")

        win = tk.Toplevel(self.root)
        win.title("Reservas registradas")
        win.geometry("750x400")
        win.transient(self.root)

        columns = ("#","Nombre", "Email", "Fecha", "Hora", "Cancha")
        tree = ttk.Treeview(win, columns=columns, show="headings", selectmode="browse")
        tree.pack(fill="both", expand=True, padx=10, pady=(10,0))

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=True, width=120)
        tree.column("#", width=30)

        for i, r in enumerate(self._reservas_simuladas, start=1):
            tree.insert("", "end", iid=i, values=(i, r["nombre"], r["email"], r["fecha"], r["hora"], r["cancha"]))

        # --- Botones debajo de la tabla ---
        btn_frame = ttk.Frame(win, padding=10)
        btn_frame.pack(fill="x")

        def editar():
            selected = tree.selection()
            if not selected:
                return messagebox.showwarning("Atención", "Selecciona una reserva para editar.")
            idx = int(selected[0]) - 1
            reserva = self._reservas_simuladas[idx]
            self._abrir_editor_reserva(reserva, idx, tree)

        def cancelar():
            selected = tree.selection()
            if not selected:
                return messagebox.showwarning("Atención", "Selecciona una reserva para eliminar.")
            idx = int(selected[0]) - 1
            confirm = messagebox.askyesno("Confirmar", "¿Deseas cancelar esta reserva?")
            if confirm:
                del self._reservas_simuladas[idx]
                self._guardar_reservas_json()
                tree.delete(selected[0])
                messagebox.showinfo("Eliminada", "Reserva cancelada correctamente.")

        ttk.Button(btn_frame, text="📝 Editar reserva", style="Accent.TButton", command=editar).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="❌ Cancelar reserva", style="Outline.TButton", command=cancelar).pack(side="left", padx=6)

    def _abrir_editor_reserva(self, reserva, idx, tree):
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Editar reserva")
        edit_win.geometry("400x350")
        edit_win.transient(self.root)

        def field(label, valor):
            ttk.Label(edit_win, text=label).pack(anchor="w", pady=(6,0))
            e = ttk.Entry(edit_win)
            e.insert(0, valor)
            e.pack(fill="x", padx=10)
            return e

        nombre_e = field("Nombre completo", reserva["nombre"])
        tel_e = field("Teléfono", reserva["telefono"])
        email_e = field("Correo electrónico", reserva["email"])

        ttk.Label(edit_win, text="Cancha").pack(anchor="w", pady=(6,0))
        cancha_var = tk.StringVar(value=reserva["cancha"])
        cancha_cb = ttk.Combobox(edit_win, textvariable=cancha_var, state="readonly")
        cancha_cb["values"] = ["Sintética", "Vóley"]
        cancha_cb.pack(fill="x", padx=10)

        ttk.Label(edit_win, text="Hora").pack(anchor="w", pady=(6,0))
        hora_var = tk.StringVar(value=reserva["hora"])
        hora_cb = ttk.Combobox(edit_win, textvariable=hora_var, state="readonly")
        hora_cb["values"] = [f"{h}:00" for h in range(10, 22)]
        hora_cb.pack(fill="x", padx=10)

        def guardar_cambios():
            reserva["nombre"] = nombre_e.get().strip()
            reserva["telefono"] = tel_e.get().strip()
            reserva["email"] = email_e.get().strip()
            reserva["cancha"] = cancha_var.get()
            reserva["hora"] = hora_var.get()
            self._reservas_simuladas[idx] = reserva
            self._guardar_reservas_json()
            edit_win.destroy()
            tree.item(idx+1, values=(idx+1, reserva["nombre"], reserva["email"], reserva["fecha"], reserva["hora"], reserva["cancha"]))
            messagebox.showinfo("Actualizada", "Reserva actualizada correctamente.")

        ttk.Button(edit_win, text="Guardar cambios", style="Accent.TButton", command=guardar_cambios).pack(pady=15)

    def ver_disponibilidad(self):
        messagebox.showinfo("Disponibilidad", "Mostrando disponibilidad (simulado)")

if __name__ == "__main__":
    root = tk.Tk()
    app = DesignApp(root)
    root.mainloop()
