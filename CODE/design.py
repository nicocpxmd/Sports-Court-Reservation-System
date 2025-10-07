"""
design_app.py
-------------
Interfaz gráfica del sistema de reservas.
Se integra con Manager (API en inglés):
 - create_reservation(...)
 - get_all_reservations() -> list[dict]
 - edit_reservation_by_id(id, **kwargs)
 - cancel_reservation_by_id(id)
 - get_price_for_court(tipo) -> float
 - get_court_types() -> list[str]
 - check_availability(cancha, fecha, hora) -> bool
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from tkcalendar import DateEntry
from datetime import date

from manager import Manager


class DesignApp:
    def __init__(self, root):
        self.root = root
        self.manager = Manager()

        self._config_root()
        self._create_styles()
        self._create_header()
        self._create_form()
        self._create_buttons()

    # -------------------------
    # Setup UI
    # -------------------------
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
        except Exception:
            pass

        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10)

        style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        style.configure("Header.TLabel", background=self.bg_color, font=self.title_font)
        style.configure("FormLabel.TLabel", background=self.card_bg, font=self.label_font, foreground="#333333")
        style.configure("Accent.TButton", background="#2b9edb", foreground="white", font=self.label_font, padding=8)
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
            ent = ttk.Entry(parent, font=self.label_font)
            ent.pack(fill="x")
            return ent

        self.nombre_entry = field(left_col, "Nombre completo")
        self.documento_entry = field(left_col, "Documento")
        self.telefono_entry = field(left_col, "Teléfono")
        self.email_entry = field(left_col, "Correo electrónico")

        ttk.Label(left_col, text="Cancha", style="FormLabel.TLabel").pack(anchor="w", pady=(10,2))
        types = self.manager.get_court_types()
        default_type = types[0] if types else ""
        self.cancha_var = tk.StringVar(value=default_type)
        self.cancha_combo = ttk.Combobox(left_col, textvariable=self.cancha_var, state="readonly")
        self.cancha_combo["values"] = types
        self.cancha_combo.pack(fill="x")

        # Container for Fecha / Hora / Precio
        container = ttk.Frame(left_col, style="Card.TFrame")
        container.pack(fill="x", pady=(10,0))

        ttk.Label(container, text="Fecha", style="FormLabel.TLabel").grid(row=0, column=0, sticky="w")
        self.fecha_picker = DateEntry(container, width=14, borderwidth=1, date_pattern='yyyy-mm-dd', mindate=date.today())
        self.fecha_picker.grid(row=1, column=0, padx=4, pady=(0,6), sticky="w")

        ttk.Label(container, text="Hora", style="FormLabel.TLabel").grid(row=0, column=1, sticky="w")
        self.hora_var = tk.StringVar()
        self.hora_combo = ttk.Combobox(container, textvariable=self.hora_var, state="readonly", width=8)
        self.hora_combo["values"] = [f"{h}:00" for h in range(10, 22)]
        self.hora_combo.grid(row=1, column=1, padx=4, pady=(0,6), sticky="w")

        ttk.Label(container, text="Precio (USD/hora)", style="FormLabel.TLabel").grid(row=0, column=2, sticky="w")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(container, textvariable=self.price_var, font=self.label_font, state="readonly", justify="left", width=12)
        self.price_entry.grid(row=1, column=2, padx=4, pady=(0,6), sticky="w")

        self.cancha_combo.bind("<<ComboboxSelected>>", lambda e: self._update_price())
        self._update_price()

    def _update_price(self):
        cancha = self.cancha_var.get()
        try:
            price = self.manager.get_price_for_court(cancha)
        except Exception:
            price = 0.0
        self.price_var.set(f"${price:.2f}")

    # -------------------------
    # Buttons
    # -------------------------
    def _create_buttons(self):
        bar = ttk.Frame(self.root, style="Card.TFrame")
        bar.place(relx=0.5, rely=0.88, anchor="n", relwidth=0.92)

        ttk.Button(bar, text="Reservar", style="Accent.TButton", command=self._reservar).pack(side="left", padx=6)
        ttk.Button(bar, text="Ver reservas", style="Outline.TButton", command=self.ver_reservas).pack(side="left", padx=6)
        ttk.Button(bar, text="Disponibilidad", style="Outline.TButton", command=self._ver_disponibilidad).pack(side="left", padx=6)

    # -------------------------
    # Main actions
    # -------------------------
    def _reservar(self):
        nombre = self.nombre_entry.get().strip()
        documento = self.documento_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        email = self.email_entry.get().strip()
        cancha = self.cancha_var.get()
        fecha = self.fecha_picker.get()
        hora = self.hora_var.get()

        if not nombre or not documento or not hora:
            return messagebox.showerror("Error", "Completa todos los campos obligatorios (nombre, documento, hora).")

        try:
            self.manager.create_reservation(
                nombre=nombre,
                documento=documento,
                telefono=telefono,
                email=email,
                cancha=cancha,
                fecha=fecha,
                hora=hora
            )
        except ValueError as e:
            return messagebox.showerror("Error", str(e))
        except Exception as e:
            return messagebox.showerror("Error inesperado", str(e))

        messagebox.showinfo("Reserva exitosa", "¡Reserva realizada con éxito!")
        self.hora_var.set("")

    def ver_reservas(self):
        reservas = self.manager.get_all_reservations()
        if not reservas:
            return messagebox.showinfo("Reservas", "No hay reservas registradas.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Reservas registradas")
        ventana.geometry("800x400")

        columnas = ("Nombre", "Email", "Fecha", "Hora", "Cancha", "Precio")
        tree = ttk.Treeview(ventana, columns=columnas, show="headings", selectmode="browse")

        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        for r in reservas:
            res_id = r["id"]
            tree.insert("", "end", iid=res_id, values=(
                r["nombre"], r["email"], r["fecha"], r["hora"], r["cancha"], f"${r['precio']:.2f}"
            ))

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def editar():
            selected = tree.selection()
            if not selected:
                return messagebox.showwarning("Atención", "Selecciona una reserva para editar.")
            res_id = selected[0]
            reserva = self.manager.get_reservation_by_id(res_id)
            if not reserva:
                return messagebox.showerror("Error", "La reserva seleccionada ya no existe.")
            self._abrir_editor_reserva(reserva, res_id, tree)

        def cancelar():
            selected = tree.selection()
            if not selected:
                return messagebox.showwarning("Atención", "Selecciona una reserva para cancelar.")
            res_id = selected[0]
            if not messagebox.askyesno("Confirmar", "¿Deseas cancelar esta reserva?"):
                return
            try:
                self.manager.cancel_reservation_by_id(res_id)
                tree.delete(res_id)
                messagebox.showinfo("Cancelada", "La reserva ha sido eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        frame_botones = tk.Frame(ventana)
        frame_botones.pack(pady=10)
        tk.Button(frame_botones, text="Editar", command=editar, width=12, bg="#007bff", fg="white").pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cancelar", command=cancelar, width=12, bg="#dc3545", fg="white").pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cerrar", command=ventana.destroy, width=12).pack(side="left", padx=10)

    def _abrir_editor_reserva(self, reserva, res_id: str, tree: ttk.Treeview):
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Editar reserva")
        edit_win.geometry("420x420")
        edit_win.transient(self.root)

        def field(label, value):
            ttk.Label(edit_win, text=label).pack(anchor="w", pady=(6,0), padx=10)
            e = ttk.Entry(edit_win)
            e.insert(0, value or "")
            e.pack(fill="x", padx=10)
            return e

        nombre_e = field("Nombre completo", reserva.client.nombre)
        tel_e = field("Teléfono", reserva.client.telefono)
        email_e = field("Correo electrónico", reserva.client.email)

        ttk.Label(edit_win, text="Cancha").pack(anchor="w", pady=(6,0), padx=10)
        cancha_var = tk.StringVar(value=reserva.court.tipo)
        cancha_cb = ttk.Combobox(edit_win, textvariable=cancha_var, state="readonly")
        cancha_cb["values"] = self.manager.get_court_types()
        cancha_cb.pack(fill="x", padx=10)

        ttk.Label(edit_win, text="Hora").pack(anchor="w", pady=(6,0), padx=10)
        hora_var = tk.StringVar(value=reserva.hora)
        hora_cb = ttk.Combobox(edit_win, textvariable=hora_var, state="readonly")
        hora_cb["values"] = [f"{h}:00" for h in range(10, 22)]
        hora_cb.pack(fill="x", padx=10)

        ttk.Label(edit_win, text="Precio (USD/hora)").pack(anchor="w", pady=(6,0), padx=10)
        edit_price_var = tk.StringVar(value=f"${self.manager.get_price_for_court(cancha_var.get()):.2f}")
        edit_price_entry = ttk.Entry(edit_win, textvariable=edit_price_var, state="readonly")
        edit_price_entry.pack(fill="x", padx=10)

        cancha_cb.bind("<<ComboboxSelected>>", lambda e: edit_price_var.set(f"${self.manager.get_price_for_court(cancha_var.get()):.2f}"))

        def guardar_cambios():
            new_data = {
                "nombre": nombre_e.get().strip(),
                "telefono": tel_e.get().strip(),
                "email": email_e.get().strip(),
                "cancha": cancha_var.get(),
                "hora": hora_var.get()
            }
            try:
                self.manager.edit_reservation_by_id(res_id, **new_data)
            except Exception as e:
                return messagebox.showerror("Error", str(e))

            updated = self.manager.get_reservation_by_id(res_id)
            if updated:
                d = updated.to_dict()
                tree.item(res_id, values=(
                    d["nombre"], d["email"], d["fecha"], d["hora"], d["cancha"], f"${d['precio']:.2f}"
                ))

            edit_win.destroy()
            messagebox.showinfo("Actualizada", "Reserva actualizada correctamente.")

        ttk.Button(edit_win, text="Guardar cambios", style="Accent.TButton", command=guardar_cambios).pack(pady=15)

    def _ver_disponibilidad(self):
        cancha = self.cancha_var.get()
        fecha = self.fecha_picker.get()
        hora = self.hora_var.get()

        if not cancha or not fecha:
            return messagebox.showwarning("Atención", "Selecciona cancha y fecha para consultar disponibilidad.")

        if not hora:
            free = [f"{h}:00" for h in range(10, 22) if self.manager.check_availability(cancha, fecha, f"{h}:00")]
            msg = f"Horas libres para {cancha} el {fecha}:\n" + (", ".join(free) if free else "No hay horas libres.")
            return messagebox.showinfo("Disponibilidad", msg)

        disponible = self.manager.check_availability(cancha, fecha, hora)
        msg = f"{cancha} {'está disponible' if disponible else 'NO está disponible'} el {fecha} a las {hora}."
        messagebox.showinfo("Disponibilidad", msg)