import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class IterationPlotter:
    def __init__(self, root, data_lists1, data_lists2):
        self.root = root
        self.data_lists1 = data_lists1
        self.data_lists2 = data_lists2
        self.current_iteration1 = 0
        self.current_iteration2 = 0

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

        self.curve1_var = tk.StringVar()
        self.curve2_var = tk.StringVar()

        self.curve1_var.set("0")
        self.curve2_var.set("0")

        self.curve1_menu = tk.OptionMenu(self.root, self.curve1_var, *range(len(data_lists1)), command=self.update_curves)
        self.curve2_menu = tk.OptionMenu(self.root, self.curve2_var, *range(len(data_lists2)), command=self.update_curves)

        self.curve1_menu.pack()
        self.curve2_menu.pack()

        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.set_title("Selected Curves")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        selected_curve1 = self.data_lists1[self.current_iteration1]
        selected_curve2 = self.data_lists2[self.current_iteration2]

        x1, y1 = zip(*selected_curve1)
        x2, y2 = zip(*selected_curve2)

        self.ax.plot(x1, y1, label="Curve 1")
        self.ax.plot(x2, y2, label="Curve 2")

        self.ax.legend()
        self.canvas.draw()

    def update_curves(self, value):
        self.current_iteration1 = int(self.curve1_var.get())
        self.current_iteration2 = int(self.curve2_var.get())
        self.update_plot()

if __name__ == "__main__":
    data_lists1 = [
        [[1, 2], [2, 4], [3, 6], [4, 8], [5, 10]],
        [[1, 1], [2, 3], [3, 5], [4, 7], [5, 9]],
        [[1, 10], [2, 8], [3, 6], [4, 4], [5, 2]]
    ]

    data_lists2 = [
        [[1, 1], [2, 3], [3, 1], [4, 3], [5, 1]],
        [[1, 2], [2, 2], [3, 2], [4, 2], [5, 2]],
        [[1, 3], [2, 1], [3, 3], [4, 1], [5, 3]]
    ]

    root = tk.Tk()
    root.title("Curve Plotter")
    app = IterationPlotter(root, data_lists1, data_lists2)
    root.mainloop()
