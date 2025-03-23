from tkinter import *

#윈도우를 만들 때 복잡한 과정들을 메소드화하는 클래스를 만든다. 그게 windowManager
class WindowManager:
    def __init__(self, title: str="Do you want some BUTTER?", resizing_x: bool=True, resizing_y: bool=True):
        self.__window = Tk()
        self.__window.title(title)
        self.__window.resizable(width=resizing_x, height=resizing_y)

    def set_size(self, geometry: str):
        self.__window.geometry(geometry)

    def main_loop_window(self):
        self.__window.mainloop()

#window = WindowManager()
#window.main_loop_window()