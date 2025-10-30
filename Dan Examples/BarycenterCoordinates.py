# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 15:56:16 2025

@author: dbied
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BarycenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matplotlib in Tkinter")

        # Layout frames
        self.control_frame = ttk.Frame(root, padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.plot_frame = ttk.Frame(root, padding=10)
        self.plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.status_frame = ttk.Frame(root, padding=10)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Entry fields for points A, B, C
        self.point_vars = {}
        for label in ['A', 'B', 'C']:
            ttk.Label(self.control_frame, text=f"Point {label}").pack(pady=(10, 0))
            x_var = tk.DoubleVar(value=0.0)
            y_var = tk.DoubleVar(value=0.0)
            self.point_vars[label] = (x_var, y_var)

            entry_frame = ttk.Frame(self.control_frame)
            entry_frame.pack(pady=2)

            ttk.Label(entry_frame, text="x:").pack(side=tk.LEFT)
            ttk.Entry(entry_frame, textvariable=x_var, width=6).pack(side=tk.LEFT)

            ttk.Label(entry_frame, text="y:").pack(side=tk.LEFT)
            ttk.Entry(entry_frame, textvariable=y_var, width=6).pack(side=tk.LEFT)

            # Add trace callbacks
            x_var.trace_add("write", lambda *_, var=x_var: self.update_plot())
            y_var.trace_add("write", lambda *_, var=y_var: self.update_plot())

        # Spacer before Point P
        ttk.Label(self.control_frame, text="").pack(pady=10)

        # Entry fields for point P
        ttk.Label(self.control_frame, text="Point P").pack(pady=(10, 0))
        self.p_x = tk.DoubleVar(value=0.0)
        self.p_y = tk.DoubleVar(value=0.0)

        p_frame = ttk.Frame(self.control_frame)
        p_frame.pack(pady=2)

        ttk.Label(p_frame, text="x:").pack(side=tk.LEFT)
        ttk.Entry(p_frame, textvariable=self.p_x, width=6).pack(side=tk.LEFT)

        ttk.Label(p_frame, text="y:").pack(side=tk.LEFT)
        ttk.Entry(p_frame, textvariable=self.p_y, width=6).pack(side=tk.LEFT)

        # Add trace callbacks for P
        self.p_x.trace_add("write", lambda *_, var=self.p_x: self.update_plot())
        self.p_y.trace_add("write", lambda *_, var=self.p_y: self.update_plot())

        # Status display for alpha, beta, gamma
        self.status_label = ttk.Label(self.status_frame, text="α = 0.0   β = 0.0   γ = 0.0", font=("Segoe UI", 12))
        self.status_label.pack()

        self.update_plot()
        
    def barycentric_coordinates(A, B, C, P):
        """
        Compute barycentric coordinates (alpha, beta, gamma) of point P
        with respect to triangle ABC.
    
        Parameters:
            A, B, C, P: tuples or lists of (x, y)
    
        Returns:
            (alpha, beta, gamma): barycentric coordinates of P
        """
        xA, yA = A
        xB, yB = B
        xC, yC = C
        xP, yP = P
    
        # Compute vectors
        v0 = (xB - xA, yB - yA)
        v1 = (xC - xA, yC - yA)
        v2 = (xP - xA, yP - yA)
    
        # Compute dot products
        d00 = v0[0]*v0[0] + v0[1]*v0[1]
        d01 = v0[0]*v1[0] + v0[1]*v1[1]
        d11 = v1[0]*v1[0] + v1[1]*v1[1]
        d20 = v2[0]*v0[0] + v2[1]*v0[1]
        d21 = v2[0]*v1[0] + v2[1]*v1[1]
    
        # Compute barycentric coordinates
        denom = d00 * d11 - d01 * d01
        if denom == 0:
            return (None, None, None)  # Degenerate triangle
    
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1 - v - w
    
        return (u, v, w)


    def compute(self):
        # Update status label (placeholder values)
        x,y = self.point_vars['A']
        A = (x.get(), y.get())
        x,y = self.point_vars['B']
        B = (x.get(), y.get())
        x,y = self.point_vars['C']
        C = (x.get(), y.get())
        P = (self.p_x.get(), self.p_y.get())
        alpha, beta, gamma = BarycenterApp.barycentric_coordinates(A, B, C, P)
        inside = True
        result = ""
        if alpha == None:
            inside = False
            result += "α = --, "
        else:
            result += f"α = {alpha:.3f}, "
            if alpha < 0:
                inside = False
        if beta == None:
            inside - False
            result += "β = --, "
        else:
            result += f"β = {beta:.3f}, "
            if beta < 0:
                inside = False
        if gamma == None:
            inside = False
            result += "γ = --"
        else:
            result += f"γ = {gamma:.3f}"
            if gamma < 0:
                inside = False

        self.status_label.config(text= result)
        return inside

    def update_plot(self):
        self.ax.clear()

        inside = self.compute()
        # Plot points A, B, C
        vx = []; vy= []
        for label, (x_var, y_var) in self.point_vars.items():
            x, y = x_var.get(), y_var.get()
            self.ax.plot(x, y, 'o', label=f"{label} ({x:.1f}, {y:.1f})")
            vx.append(x); vy.append(y)
        
        vx.append(vx[0]); vy.append(vy[0])
        self.ax.plot(vx, vy, 'k-', label="Triangle")

        # Plot point P
        px, py = self.p_x.get(), self.p_y.get()
        if inside:
            self.ax.plot(px, py, '+', color='green', label=f"P ({px:.1f}, {py:.1f})")
        else:
            self.ax.plot(px, py, 'x', color='red', label=f"P ({px:.1f}, {py:.1f})")

        self.ax.legend()
        #self.ax.set_xlim(-10, 10)
        #self.ax.set_ylim(-10, 10)
        self.ax.set_title("Points A, B, C and P")
        self.ax.grid(True)
        self.canvas.draw()

       

if __name__ == "__main__":
    root = tk.Tk()
    app = BarycenterApp(root)
    root.mainloop()