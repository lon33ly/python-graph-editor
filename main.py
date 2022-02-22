import tkinter as tk
import math
import constants
from dialog import askstring
from tkinter import simpledialog
from enum import Enum, auto
from constants import *
from structures import *


# нужен для отслеживания статуса работы с программой
class EditingMode(Enum):
    DEFAULT = auto()
    DELETING_ELEMENT = auto()
    CONNECTING = auto()


class DragAndDropArea(tk.Canvas):
    def __init__(self, master, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.active = None
        self.active_text = None
        self.selected_vertices = list()
        self.editing_mode = EditingMode.DEFAULT
        self.vertex_size = 100
        self.created_vertices = list()
        self.shift_length = 80
        self.count_vertices = 0

        # colors
        self.edge_weight_text_color = 'white'
        self.default_color = 'red'
        self.selecting_color = '#638ae6'  # синий
        self.edge_color = '#ab7738'  # зеленый

        # default tags for elements
        self.edge_tag = 'edge'
        self.vertex_tag = 'vertex'
        self.vertex_text_tag = 'vertex_text'
        self.weight_bg_tag = 'weight_bg'
        self.weight_tag = 'weight'

        # bind actions to mouse
        self.bind('<ButtonPress-1>', self.get_item)
        self.bind('<B1-Motion>', self.move_active)
        self.bind('<ButtonRelease-1>', self.set_none)
        self.bind("<Button-2>", self.do_popup)

        # бинды на клавиатуру
        # добавить обработку на русской и не русской раскладке и в разном написании капосом и не капсом
        self.bind('<KeyPress-s>', self.switch_mode)

        # меню
        self.vertex_menu = tk.Menu(self, tearoff=0)
        self.vertex_menu.add_command(label="Удалить вершину", command=self.delete_element)
        self.vertex_menu.add_separator()

        self.edge_menu = tk.Menu(self, tearoff=0)
        self.edge_menu.add_command(label="Удалить грань", command=self.delete_element)

        self.default_menu = tk.Menu(self, tearoff=0)
        self.default_menu.add_command(label="Создать вершину", command=self.create_vertex)
        self.default_menu.add_command(label="Соеднить вершины")

        # отображение дополнительной информации
        self.create_text(10, 10, fill='black', text="текущий режим",
                         font=f"Courier_new {20} bold", anchor=tk.NW)
        self.status_show = self.create_text(10, 40, fill=self.edge_color, text="редактирование",
                                            font=f"Courier_new {20} bold", anchor=tk.NW)

    # запуск меню в зависимости от нажатого элемента на экране
    def do_popup(self, event):
        try:
            vertex = self.find_withtag(f'current&&{self.vertex_tag}')
            edge = self.find_withtag(f'current&&{self.edge_tag}')
            if len(vertex):
                self.vertex_menu.tk_popup(event.x_root, event.y_root)
            elif len(edge):
                self.edge_menu.tk_popup(event.x_root, event.y_root)
            else:
                self.default_menu.tk_popup(event.x_root, event.y_root)

        except IndexError:
            print("oy")

    # снятие активного положения с вершины (нужно для перемещения)
    def set_none(self, event):
        self.active = None
        self.active_text = None

    # "касание" вершины для перемещения или выделения
    def get_item(self, event):
        try:
            if self.editing_mode == EditingMode.DEFAULT:
                vertex = self.find_withtag(f'current&&{self.vertex_tag}')
                self.active = vertex[0]
                text = self.find_withtag(self.vertex_text_tag+str(self.active))
                self.active_text = text[0]
            elif self.editing_mode == EditingMode.CONNECTING:
                self.connecting_selected_edges()
        except IndexError:
            print('Никакой элемент не был нажат')

    def move_active(self, event):
        if self.active is not None:
            coords = self.coords(self.active)
            width = coords[2] - coords[0]  # x2-x1
            height = coords[1] - coords[3]  # y1-y2

            x1 = event.x - width / 2
            y1 = event.y - height / 2
            x2 = event.x + width / 2
            y2 = event.y + height / 2
            txt_x = event.x
            txt_y = event.y

            self.coords(self.active, x1, y1, x2, y2)
            self.coords(self.active_text, txt_x, txt_y)
            try:
                self.update_tension(self.active)
            except IndexError:
                print('Связей между вершинами не найдено')

    # обновление линии которая связывает вершины
    def update_tension(self, tag):
        tensions = self.find_withtag(self.vertex_tag+str(tag))
        for tension in tensions:
            bounded_cards = self.gettags(tension)
            weight_edge = self.find_withtag(self.weight_tag+str(tension))[0]
            bg_weight_edge = self.find_withtag(self.weight_bg_tag+str(weight_edge))[0]
            vertex1 = bounded_cards[0].replace(self.vertex_tag, '')
            vertex2 = bounded_cards[1].replace(self.vertex_tag, '')
            x1, y1 = self.get_mid_point(vertex1)
            x2, y2 = self.get_mid_point(vertex2)
            if bounded_cards[3] == 'directed':
                shift = self.calculate_shift(x1, y1, x2, y2)
                x_shift, y_shift, x_shift_weight, y_shift_weight, x_m, y_m = \
                    shift[0], shift[1], shift[2], shift[3], shift[4], shift[5]

                angle = self.calculate_angle(x1, y1, x2, y2)
                x_shift_d = abs(math.cos(math.radians(90 - abs(angle))) * self.vertex_size / 2)
                y_shift_d = abs(math.cos(math.radians(abs(angle))) * self.vertex_size / 2)

                if x2 <= x1 and y2 < y1:
                    x2 = x2 + x_shift_d
                    y2 = y2 + y_shift_d
                if x2 > x1 and y2 <= y1:
                    x2 = x2 - x_shift_d
                    y2 = y2 + y_shift_d
                if x2 >= x1 and y2 > y1:
                    x2 = x2 - x_shift_d
                    y2 = y2 - y_shift_d
                if x2 < x1 and y2 >= y1:
                    x2 = x2 + x_shift_d
                    y2 = y2 - y_shift_d
                self.coords(tension, x1, y1, x_shift, y_shift, x2, y2)

                self.coords(weight_edge, x_m+x_shift_weight*0.55, y_m+y_shift_weight*0.55)
                self.coords(bg_weight_edge, self.bbox(weight_edge))
            else:
                self.coords(tension, x1, y1, x2, y2)
                self.coords(weight_edge, (x1+x2)/2, (y1+y2)/2)
                self.coords(bg_weight_edge, self.bbox(weight_edge))

            self.lower(tension)

    # создание вершины
    def draw_vertex(self, x, y, width, height, color):
        x1, y1 = x, y
        x2, y2 = x + width, y + height
        oval = self.create_oval(x1, y1, x2, y2, fill=color, tags=(self.vertex_tag,))

        return oval

    # выстраивание связи между двумя гранями визуально
    def bind_tension(self, vertex, another_vertex, weight, directed=True):
        x1, y1 = self.get_mid_point(vertex)
        x2, y2 = self.get_mid_point(another_vertex)
        tag1 = self.vertex_tag+str(vertex)
        tag2 = self.vertex_tag+str(another_vertex)
        shift = self.calculate_shift(x1, y1, x2, y2)
        x_shift = shift[0]
        y_shift = shift[1]
        x_shift_d = shift[2]*0.6+shift[4]
        y_shift_d = shift[3]*0.6+shift[5]
        unique_answer = self.check_unique_tensions(tag1, tag2)

        if directed and unique_answer[0]:
            line = self.create_line(x1, y1,
                                    x_shift,
                                    y_shift,
                                    x2, y2,
                                    fill=self.edge_color, width=10,
                                    tags=(tag1, tag2, self.edge_tag, 'directed'), smooth=1, arrow=tk.LAST,
                                    arrowshape=(30, 30, 10), )

            text_weight = self.create_text(x_shift_d, y_shift_d, text=weight, state=tk.DISABLED,
                                           fill='black', tags=(self.weight_tag + str(line),),
                                           font=f"Courier_new {int(self.vertex_size / 3.7)} normal")

            back_g = self.make_bg_weight(text_weight)
            self.tag_lower(back_g, text_weight)
            self.update_tension(vertex)

            self.lower(line)

        if not directed and unique_answer[1]:
            line = self.create_line(x1, y1, x2, y2, fill=self.edge_color, width=10,
                                    tags=(tag1, tag2, self.edge_tag, 'undirected'), )

            text_weight = self.create_text((x1+x2)/2, (y1+y2)/2, text=weight, state=tk.DISABLED,
                                           fill='black', tags=(self.weight_tag + str(line),),
                                           font=f"Courier_new {int(self.vertex_size / 3.7)} normal")

            back_g = self.make_bg_weight(text_weight)
            self.tag_lower(back_g, text_weight)
            self.update_tension(vertex)

            self.lower(line)

    def check_unique_tensions(self, tag1, tag2):
        directed, undirected = True, True
        for tension in self.find_withtag(tag1):
            tags = self.gettags(tension)
            if tag1 in tags and tag2 in tags:
                if tags[3] == 'undirected':
                    undirected = False
                    directed = False
                else:
                    if tag1 == tags[0] and tag2 == tags[1]:
                        undirected = False
                        directed = False
                    else:
                        undirected = False

        return directed, undirected

    def make_bg_weight(self, text_weight):
        back_g = self.create_rectangle(self.bbox(text_weight),
                                       fill=self.edge_color, state=tk.DISABLED,
                                       outline=self.edge_color, width=5,
                                       tags=(self.weight_bg_tag + str(text_weight),))

        return back_g

    # вычисление координат середины карточки отвечающей за вершину графа
    def get_mid_point(self, vertex):
        coords = self.coords(vertex)
        width = coords[2] - coords[0]  # x2-x1
        height = coords[1] - coords[3]  # y1-y2
        position = coords[0], coords[1]  # x1,y1

        mid_x = position[0] + width / 2
        mid_y = position[1] - height / 2

        return mid_x, mid_y

    # смена режима с выбора вершин и обычного, в котором их можно перемещать
    def switch_mode(self, e):
        if self.editing_mode == EditingMode.DEFAULT:
            self.editing_mode = EditingMode.CONNECTING
            self.update_status_bar()
        elif self.editing_mode == EditingMode.CONNECTING:
            for vertex in self.selected_vertices:
                self.itemconfig(vertex, fill=self.default_color)
            self.selected_vertices.clear()
            self.editing_mode = EditingMode.DEFAULT
            self.update_status_bar()

    # удаление элемента
    def delete_element(self, event=None):
        element = self.find_withtag('current')[0]
        tags_of_element = self.gettags(element)
        if self.vertex_tag in tags_of_element:
            self.delete(element)
            text = self.find_withtag(self.vertex_text_tag+str(element))[0]
            self.delete(text)
            tensions = self.find_withtag(self.vertex_tag+str(element))
            for tension in tensions:
                self.delete(tension)
                for weight in self.find_withtag(self.weight_tag+str(tension)):
                    self.delete(weight)
                    self.delete(self.find_withtag(self.weight_bg_tag+str(weight)))

        elif self.edge_tag in tags_of_element:
            self.delete(element)
            for weight in self.find_withtag(self.weight_tag + str(element)):
                self.delete(weight)
                self.delete(self.find_withtag(self.weight_bg_tag + str(weight)))

    def update_status_bar(self):
        if self.editing_mode == EditingMode.CONNECTING:
            self.itemconfig(self.status_show, fill=self.selecting_color, text='соединение')
        elif self.editing_mode == EditingMode.DEFAULT:
            self.itemconfig(self.status_show, fill=self.edge_color, text='редактирование')

    # создание вершины с текстом и фигуркой
    def create_vertex(self):
        x, y = self.winfo_pointerx() - self.winfo_rootx(), self.winfo_pointery() - self.winfo_rooty()
        x = x - self.vertex_size / 2
        y = y - self.vertex_size / 2
        tx = x + self.vertex_size / 2
        ty = y + self.vertex_size / 2

        self.count_vertices += 1
        vertex = self.draw_vertex(x, y, self.vertex_size, self.vertex_size, self.default_color)
        self.create_text(tx, ty, font=f"Courier_new {int(self.vertex_size/2)} normal",
                         text=f"{self.count_vertices}",
                         fill='black',
                         state=tk.DISABLED, tags=(self.vertex_text_tag+str(vertex),))

    # соединение выбранных двух вершин в режиме выделения
    def connecting_selected_edges(self):
        vertex = self.find_withtag(f'current&&{self.vertex_tag}')[0]
        print(vertex)
        if vertex not in self.selected_vertices:
            self.itemconfig(vertex, fill=self.selecting_color)
            self.selected_vertices.append(vertex)
            if len(self.selected_vertices) == 2:
                answer = askstring(title="Настройка связи вершин", parent=self,
                                   prompt="Настройка связи вершин")
                if answer[1] == constants.DIRECTED:
                    edge_type = True
                else:
                    edge_type = False
                    print("Undirected")

                self.bind_tension(self.selected_vertices[0], self.selected_vertices[1], answer[0], directed=edge_type)
                for vertex in self.selected_vertices:
                    self.itemconfig(vertex, fill=self.default_color)
                self.selected_vertices.clear()
        else:
            self.itemconfig(vertex, fill=self.default_color)
            self.selected_vertices.remove(vertex)

    # статический метод высчитывания угла наклона прямой
    @staticmethod
    def calculate_angle(x1, y1, x2, y2):
        if x2 - x1 == 0:
            m = 0
        elif y2 - y1 == 0:
            m = math.inf
        else:
            m = 1 / ((y2 - y1) / (x2 - x1))

        angle = math.degrees(math.atan(m))

        return angle

    # метод высчитывания сдвига для построение точки отклонения направленного ребра
    def calculate_shift(self, x1, y1, x2, y2):
        mid_line_x = (x1 + x2) / 2
        mid_line_y = (y1 + y2) / 2

        angle = self.calculate_angle(x1, y1, x2, y2)

        x_shift_d = abs(math.cos(math.radians(abs(angle))) * self.shift_length)
        y_shift_d = abs(math.cos(math.radians(90 - abs(angle))) * self.shift_length)

        if x2 <= x1 and y2 < y1:
            x_shift_d = x_shift_d
            y_shift_d = (-1)*y_shift_d
        if x2 > x1 and y2 <= y1:
            x_shift_d = x_shift_d
            y_shift_d = y_shift_d
        if x2 >= x1 and y2 > y1:
            x_shift_d = (-1)*x_shift_d
            y_shift_d = y_shift_d
        if x2 < x1 and y2 >= y1:
            x_shift_d = (-1)*x_shift_d
            y_shift_d = (-1)*y_shift_d

        return mid_line_x+x_shift_d, mid_line_y+y_shift_d, x_shift_d, y_shift_d, mid_line_x, mid_line_y


if __name__ == "__main__":
    window = tk.Tk()
    window.state('zoomed')
    area = DragAndDropArea(window, bg='white')
    area.pack(fill='both', expand=1)

    # нужно сделать фокусировку чтобы работало биндинг кнопок клавиатуры (клавиши)
    area.focus_set()
    window.mainloop()

