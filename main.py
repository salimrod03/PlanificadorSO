import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from Planificador import run_simulation
from Procesos import Process
from Recursos import Recurso

CPUS = 4
TOTAL_RECURSOS = 10
recursos_global = Recurso("Recurso Global", TOTAL_RECURSOS)

class ProcessManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Planificación de Procesos")
        

        self.processes = []
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=10)

        # tabla de procesos
        self.tree = ttk.Treeview(frame, columns=("PID", "Llegada", "Ejecución", "Prioridad", "Recursos", "Estado"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # agregar procesos
        form = tk.Frame(self.root)
        form.pack(pady=10)

        tk.Label(form, text="Tiempo de Ejecución:").grid(row=0, column=0)
        self.burst_entry = tk.Entry(form)
        self.burst_entry.grid(row=0, column=1)

        tk.Label(form, text="Prioridad:").grid(row=1, column=0)
        self.priority_entry = tk.Entry(form)
        self.priority_entry.grid(row=1, column=1)

        tk.Label(form, text="Recursos Necesarios:").grid(row=2, column=0)
        self.resources_entry = tk.Entry(form)
        self.resources_entry.grid(row=2, column=1)

        tk.Button(form, text="Agregar Proceso", command=self.add_process).grid(row=3, column=0, columnspan=2, pady=5)

        # botones de control
        controls = tk.Frame(self.root)
        controls.pack(pady=10)

        tk.Button(controls, text="Ejecutar Simulación", command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Eliminar Proceso", command=self.delete_process).pack(side=tk.LEFT, padx=5)

        # Selector de planificador
        tk.Label(controls, text="Planificador:").pack(side=tk.LEFT, padx=5)
        self.scheduler_choice = ttk.Combobox(controls, values=["FIFO", "SJF", "Round Robin", "Prioridad"])
        self.scheduler_choice.pack(side=tk.LEFT, padx=5)


    def add_process(self):
        try:
            burst_time = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())
            resources = int(self.resources_entry.get())

            if resources > TOTAL_RECURSOS:
                messagebox.showerror("Error", "Recursos solicitados exceden el total disponible.")
                return

            pid = len(self.processes) + 1
            process = Process(pid=pid, tiempo_llegada=0, tiempo_ejecucion=burst_time, prioridad=priority, recursos_necesarios=resources)
            self.processes.append(process)

            self.tree.insert("", "end", values=(pid, 0, burst_time, priority, resources, process.estado))
            self.clear_entries()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos.")

    def delete_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un proceso para eliminar.")
            return

        for item in selected_item:
            pid = int(self.tree.item(item, "values")[0])
            self.processes = [p for p in self.processes if p.pid != pid]
            self.tree.delete(item)

    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para simular.")
            return

        choice_map = {"FIFO": 1, "SJF": 2, "Round Robin": 3, "Prioridad": 4}
        choice = self.scheduler_choice.get()
        if choice not in choice_map:
            messagebox.showerror("Error", "Seleccione un planificador válido.")
            return

        choice_code = choice_map[choice]
        quantum = None
        if choice_code == 3:  # Round Robin
            quantum = simpledialog.askinteger("Quantum", "Ingrese el valor de Quantum:")
            if quantum is None or quantum <= 0:
                messagebox.showerror("Error", "Quantum no válido.")
                return

        try:
            run_simulation(self.processes, recursos_global, CPUS, choice_code, quantum)
            self.update_process_table()
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error durante la simulación: {e}")


    def update_process_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for process in self.processes:
            self.tree.insert("", "end", values=(process.pid, process.tiempo_llegada, process.tiempo_ejecucion,
                                                process.prioridad, process.recursos_necesarios, process.estado))

    def clear_entries(self):
        self.burst_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.resources_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessManagerApp(root)
    root.mainloop()
