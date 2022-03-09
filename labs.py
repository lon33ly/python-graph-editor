import math


class BranchAndBound:
    def __init__(self):
        self.maxsize = float('inf')
        self.N = int()
        self.final_path = [None] * (self.N + 1)
        self.final_res = self.maxsize

    def print_solution(self, adj):
        self.tsp(adj)
        print("Минимальная стоимость :", self.final_res)
        print("Пройденный путь : ", end=' ')
        for i in range(self.N + 1):
            print(self.final_path[i], end=' ')

    # функция для копирования временного решения для финального решения
    def copy_to_final(self, curr_path):
        self.final_path[:self.N + 1] = curr_path[:]
        self.final_path[self.N] = curr_path[0]

    # функция для поиска минимальной стоимости ребра имея на конце вершину i
    def first_min(self, adj, i):
        minimal = self.maxsize
        for k in range(self.N):
            if adj[i][k] < minimal and i != k:
                minimal = adj[i][k]

        return minimal

    # функция для поиска второй минимальной стоимости ребра имея на конце вершину i
    def second_min(self, adj, i):
        first, second = self.maxsize, self.maxsize
        for j in range(self.N):
            if i == j:
                continue
            if adj[i][j] <= first:
                second = first
                first = adj[i][j]

            elif (adj[i][j] <= second and
                  adj[i][j] != first):
                second = adj[i][j]

        return second

    # функция, что принимает как аргументы: curr_bound -> нижняя граница корня узла,
    # curr_weight-> хранит вес пути как далеко,
    # level-> текущий уровень пока движемся в поиске свободы дерева
    # curr_path[] -> где решение будет находится
    # которая, позже будет скопирована в final_path[]
    def tsprec(self, adj, curr_bound, curr_weight,
               level, curr_path, visited):

        # базовый случай, когда мы достигли уровня N
        # что означает, что мы покрыли все узлы один раз

        if level == self.N:

            # проверяем, есть ли ребро из
            # последней вершина на пути к первой вершине
            if adj[curr_path[level - 1]][curr_path[0]] != 0:

                # curr_res имеет общий вес
                # решения, которое мы получили
                curr_res = curr_weight + adj[curr_path[level - 1]][curr_path[0]]
                if curr_res < self.final_res:
                    self.copy_to_final(curr_path)
                    self.final_res = curr_res
            return

        # для любого другого уровня итерация для всех вершин
        # для рекурсивного построения дерева пространства поиска
        for i in range(self.N):

            # Рассмотрим следующую вершину, если она не такая же
            # (диагональная запись в матрице смежности и
            # не посещали уже)
            if (adj[curr_path[level - 1]][i] != 0 and
                    visited[i] is False):
                temp = curr_bound
                curr_weight += adj[curr_path[level - 1]][i]

                # другое вычисление curr_bound
                # для уровня 2 с других уровней
                if level == 1:
                    curr_bound -= ((self.first_min(adj, curr_path[level - 1]) +
                                    self.first_min(adj, i)) / 2)
                else:
                    curr_bound -= ((self.second_min(adj, curr_path[level - 1]) +
                                    self.first_min(adj, i)) / 2)

                # curr_bound + curr_weight фактическая нижняя граница
                # для узла, на который мы прибыли.
                # Если текущая нижняя граница < final_res,
                # нам нужно изучить узел дальше
                if curr_bound + curr_weight < self.final_res:
                    curr_path[level] = i
                    visited[i] = True

                    # вызов tsprec для следующего уровня
                    self.tsprec(adj, curr_bound, curr_weight,
                                level + 1, curr_path, visited)

                # В противном случае мы должны обрезать узел, сбросив
                # все изменения в curr_weight и curr_bound
                curr_weight -= adj[curr_path[level - 1]][i]
                curr_bound = temp

                # Также сбрасываем посещаемый массив
                visited = [False] * len(visited)
                for j in range(level):
                    if curr_path[j] != -1:
                        visited[curr_path[j]] = True

    # Эта функция устанавливает final_path
    # tsp от Travelling salesman problem
    def tsp(self, adj):
        self.N = len(adj)
        # Рассчитать начальную нижнюю границу для корневого узла
        # по формуле 1/2 * (сумма первой минуты +
        # вторая минута) для всех ребер. Также инициализируйте
        # curr_path и посещенный массив
        curr_bound = 0
        curr_path = [-1] * (self.N + 1)
        visited = [False] * self.N

        # Вычислить начальную границу
        for i in range(self.N):
            curr_bound += (self.first_min(adj, i) +
                           self.second_min(adj, i))

        # Округление нижней границы до целого числа
        curr_bound = math.ceil(curr_bound / 2)

        # Мы начинаем с вершины 1, поэтому первая вершина
        # в curr_path[] равен 0
        visited[0] = True
        curr_path[0] = 0

        # Вызов tsprec для curr_weight
        # равно 0 и уровень 1
        self.tsprec(adj, curr_bound, 0, 1, curr_path, visited)
