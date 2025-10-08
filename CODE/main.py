# Juan David Ocampo Gutierrez
# Nicolás Castro Pacheco
# Michell Valencia Berdugo
# Juan David Rivera Durán


"""
main.py
-------

Punto de entrada principal del sistema de reservas de canchas.
Inicia la interfaz gráfica DesignApp y carga los datos persistidos.
"""

import tkinter as tk
from design import DesignApp

def main():
    """Inicializa la aplicación de reservas."""
    root = tk.Tk()
    app = DesignApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()