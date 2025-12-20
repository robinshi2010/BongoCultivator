import sys
from PyQt6.QtWidgets import QApplication
from src.pet_window import PetWindow

def main():
    app = QApplication(sys.argv)
    
    # 可以在这里做一些全局配置，比如样式表
    
    pet = PetWindow()
    pet.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
