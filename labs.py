class TreeElement:
    def __init__(self):
        # будет содержать tuple (нач. вершина, кон. вершина,
        # H оценки)
        self.left = None
        self.right = None


class TestMatrices:
    m1 = [[0, 3, 5, 4, 5, 3, 27],
          [3, 0, 4, 19, 2, 5, 15],
          [5, 4, 0, 3, 4, 5, 4],
          [4, 19, 3, 0, 21, 4, 26],
          [5, 2, 4, 21, 0, 18, 5],
          [3, 5, 5, 4, 18, 0, 26],
          [27, 15, 4, 26, 5, 26, 0]]

    m2 = [[0, 1, 1, 7],
          [1, 0, 20, 1],
          [1, 20, 0, 1],
          [7, 1, 1, 0]]

    m3 = [[0, 1, 6, 3],
        [1, 0, 1, 9],
        [6, 1, 0, 1],
        [3, 9, 1, 0]]


class BranchAndBound:
    def __init__(self, adj: list):
        self.max_value = float('inf')
        self.n = len(adj)
        self.adj = self.prepare_adj_matrix(adj)
        self.H = 0

        # будет хранить tuple вида index_i, index_j, mark
        # для нулей
        self.zeros_and_marks = list()

    # подготавливаем матрицу
    # меняем нули на бесконечность, расширяем ее на 1
    # в обе стороны для хранения di и dj
    def prepare_adj_matrix(self, adj):
        for i in range(self.n):
            for j in range(self.n):
                if j == self.n-1:
                    adj[i].append(self.max_value)
            adj[i][i] = self.max_value
        adj.append([self.max_value for i in range(self.n+1)])

        return adj

    # ищем минимальные элементы в строках и выписываем
    # их в ту же таблицу справа, т.к она расширена
    def find_min_to_di(self):
        for i in range(self.n):
            minimum = self.max_value
            for j in range(self.n):
                if self.adj[i][j] < minimum:
                    minimum = self.adj[i][j]
            self.adj[i][self.n] = minimum

    # то же самое что и функция выше, только для столбцов
    # и значения помещаются снизу
    def find_min_to_dj(self):
        for i in range(self.n):
            minimum = self.max_value
            for j in range(self.n):
                if self.adj[j][i] < minimum:
                    minimum = self.adj[j][i]
            self.adj[self.n][i] = minimum

    # редуцирование по строкам
    def reduce_i(self):
        for i in range(self.n):
            for j in range(self.n):
                self.adj[i][j] = self.adj[i][j] - self.adj[i][self.n]

    # редуцирование по столбцам
    def reduce_j(self):
        for i in range(self.n):
            for j in range(self.n):
                self.adj[i][j] = self.adj[i][j] - self.adj[self.n][j]

    # оценить все нули
    def mark_zeros_all(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.adj[i][j] == 0:
                    self.zeros_and_marks.append((i, j, self.mark_zeros(i, j)))

    # вспомогательная функция для оценки всех нулей
    def mark_zeros(self, ind, j):
        # минимальный в строке с нулем
        sample_row = self.adj[ind].copy()
        sample_row.pop(j)
        min_i = min(sample_row)
        min_j = self.max_value
        # минимальный в столбце с нулем
        for i in range(self.n):
            if i == ind:
                continue
            if self.adj[i][j] < min_j:
                min_j = self.adj[i][j]

        return min_i + min_j

    def sum_of_di_and_dj(self):
        dj_sum = sum(self.adj[self.n][0:-1])
        di_sum = 0
        for i in range(self.n):
            di_sum += self.adj[i][self.n]

        return di_sum + dj_sum

    def find_max_zero(self):
        max_mark = max(self.zeros_and_marks, key=lambda pack: pack[2])
        return max_mark

    def calculate_root(self):
        self.find_min_to_di()
        self.reduce_i()
        self.find_min_to_dj()
        self.reduce_j()
        self.sum_of_di_and_dj()
        print(self.sum_of_di_and_dj())

    # должна быть рекурсивная функция которая бы принимала дугу
    def tsp(self):
        pass


if __name__ == '__main__':
    for i in enumerate(TestMatrices.m1):
        print(i)
