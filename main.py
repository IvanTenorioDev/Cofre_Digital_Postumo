import tkinter as tk
from models.cofre_model import CofreDigitalModel
from controllers.cofre_controller import CofreController
from views.main_view import CofreDigitalView

def main():
    # Inicialização em MVC
    app = tk.Tk()
    app.title("Cofre Digital Póstumo")
    
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