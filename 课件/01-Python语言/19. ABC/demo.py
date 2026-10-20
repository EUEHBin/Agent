from abc import ABC, abstractmethod


class Animal(ABC):  # 继承 ABC，表示这是一个抽象类
    @abstractmethod
    def speak(self):
        """子类必须实现这个方法"""
        pass
