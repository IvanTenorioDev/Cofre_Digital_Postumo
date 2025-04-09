import tkinter as tk
from models.cofre_model import CofreDigitalModel
from controllers.cofre_controller import CofreController
from views.main_view import CofreDigitalView
from views.styles import BG_COLOR

def main():
    # Inicialização em MVC
    app = tk.Tk()
    app.title("Cofre Digital Póstumo")
    app.geometry("900x800")  # Aumentar a altura da janela
    app.minsize(900, 800)    # Aumentar o tamanho mínimo também
    app.configure(bg=BG_COLOR)
    
    # Configuração padrão de aparência
    model = CofreDigitalModel()
    controller = CofreController()
    view = CofreDigitalView(app, controller)
    
    # Conectar view ao controller
    controller.conectar_view(view)
    
    # Iniciar o sistema
    controller.iniciar_sistema()
    
    # Iniciar aplicação
    app.mainloop()

if __name__ == "__main__":
    main() 