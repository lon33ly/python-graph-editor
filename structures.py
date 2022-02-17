class Prop:  # Prop - properties ( свойства ), от него будут наследоваться общие методы для стека и очереди

    def __init__(self):  # ключевой метод ( конструктор класса )
        super().__init__()  # инициализируем конструктор для всех дочерних классов
        self.vessel = []  # vessel - с англ. - сосуд

    def push(self, *args):  # добавляем элемент // *args позволяет принимать аргументы списком
        for element in args:
            self.vessel.append(element)

    def is_empty(self):  # проверяем на то, пусто ли
        if self.size() == 0:
            return True
        return False

    def size(self):  # считаем размер
        return len(self.vessel)

    def show(self):  # возвращаем саму структуру c елементами
        return self.vessel


class Stack(Prop):  # Last-In/First-Out ( LIFO ) Стек

    def pop(self):  #
        if self.is_empty():
            return "Стек пуст!"
        else:
            peek_el = self.vessel[-1]
            self.vessel.pop()
            return peek_el  # вернет элемент, расположенный на верху стека


class Queue(Prop):  # First-In/First-Out ( FIFO ) Очередь

    def pop(self):  #
        if self.is_empty():
            return "Очередь пуста!"
        else:
            peek_el = self.vessel[0]
            self.vessel.pop(0)
            return peek_el  # вернет элемент, расположенный первый в очереди
