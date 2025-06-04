from menus.main_menu import MainMenu
from features.handler import Handler

def run_main_menu(handler):
    while True:
        choice = MainMenu.display_main_menu()
        handler.main_menu(choice)

if __name__ == "__main__":
    handler = Handler()
    if MainMenu.display_welcome():
        handler.configure_requirements()

    run_main_menu(handler)