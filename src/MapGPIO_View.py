import MapGPIO_Controller
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo


#***********************************************************#
def inicializar_modulo_tkinter():
    
    root = tk.Tk()
    root.title('MapGPIO')

    # Tamanho da Tela
    window_width  = 800
    window_height = 600

    # Pegando resolução do monitor
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Encontrando o ponto central
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)

    # Posicionando o janela principal no centro do monitor
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Desabilitante resizing
    root.resizable(False, False)

    # Nivel de transparencia da tela de 0 (tranparente) a 1 (nitido)
    root.attributes('-alpha', 0.5)

    return root

#***********************************************************#
if __name__ == "__main__":

    root = inicializar_modulo_tkinter()

    frame1 = ttk.Frame(root, padding=20)
    frame1.grid()

    ttk.Label(frame1, text="Mapeamentos da GPIO").grid(column=0, row=0)
    ttk.Button(frame1, text="Novo", command=root.destroy).grid(column=0, row=1)
    ttk.Button(frame1, text="Carregar", command=root.destroy).grid(column=0, row=2)
    

    root.mainloop()

