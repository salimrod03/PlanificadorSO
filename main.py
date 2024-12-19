import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from Procesos import Process
from Recursos import Recurso
from Graficas import calculate_metrics

import time

CPUS = 4
TOTAL_RECURSOS = 10
recursos_global = Recurso("Recurso Global", TOTAL_RECURSOS)

def detect_deadlock(processes):
    blocked_processes = [p for p in processes if p.estado == "BLOCKED"]
    if blocked_processes:
        print("Se detectaron procesos bloqueados.")
        time.sleep(2)
        for p in blocked_processes:
            print(f"Resolviendo interbloqueo para el proceso {p.pid}.")
            p.set_estado("EVACUATED")
            p.completion_time = None
            time.sleep(2)

class ProcessManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Planificación de Procesos")

        self.processes = []
        self.running_process = None
        self.canvas_processes = []
        self.available_resources = TOTAL_RECURSOS
        self.available_cpus = CPUS
        
        self.setup_ui()
        self.update_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=10)

        # Visualización de recursos y CPUs disponibles
        self.status_label = tk.Label(
            self.root,
            text=f"Recursos disponibles: {self.available_resources}/{TOTAL_RECURSOS} - CPUs disponibles: {self.available_cpus}/{CPUS}",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(pady=10)

        # Tabla de procesos
        self.tree = ttk.Treeview(frame, columns=("PID", "Llegada", "Ejecución", "Prioridad", "Recursos", "Estado", "Tiempo Restante"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas para animaciones
        self.canvas = tk.Canvas(self.root, width=600, height=200, bg="white")
        self.canvas.pack(pady=10)

        # Formulario para agregar procesos
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

        # Botones de control
        controls = tk.Frame(self.root)
        controls.pack(pady=10)

        self.scheduler_selection = ttk.Combobox(controls, state="readonly", values=["FIFO", "SJF", "Round Robin", "Priority"])
        self.scheduler_selection.set("FIFO")
        self.scheduler_selection.pack(side=tk.LEFT, padx=5)

        tk.Button(controls, text="Ejecutar", command=self.run_selected_scheduler).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Eliminar Proceso", command=self.delete_process).pack(side=tk.LEFT, padx=5)

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
            process.tiempo_restante = burst_time
            self.processes.append(process)

            self.tree.insert("", "end", values=(pid, 0, burst_time, priority, resources, "READY", burst_time))
            self.add_to_canvas(process)
            self.clear_entries()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores válidos.")

    def add_to_canvas(self, process):
        x = 20 + len(self.canvas_processes) * 50
        rect = self.canvas.create_rectangle(x, 50, x + 40, 90, fill="blue")
        text = self.canvas.create_text(x + 20, 70, text=f"P{process.pid}\n{process.tiempo_restante}s", fill="white")
        self.canvas_processes.append((process, rect, text))

    def delete_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un proceso para eliminar.")
            return

        for item in selected_item:
            pid = int(self.tree.item(item, "values")[0])
            self.processes = [p for p in self.processes if p.pid != pid]
            self.tree.delete(item)

            # Eliminar del canvas
            self.canvas_processes = [
                (p, rect, text)
                for p, rect, text in self.canvas_processes
                if p.pid != pid
            ]
            self.canvas.delete("all")
            for i, (p, rect, text) in enumerate(self.canvas_processes):
                x = 20 + i * 50
                rect = self.canvas.create_rectangle(x, 50, x + 40, 90, fill="blue")
                text = self.canvas.create_text(x + 20, 70, text=f"P{p.pid}\n{p.tiempo_restante}s", fill="white")
                self.canvas_processes[i] = (p, rect, text)


    def update_canvas(self):
        for process, rect, text in self.canvas_processes:
            self.canvas.itemconfig(text, text=f"P{process.pid}\n{process.tiempo_restante}s")


    def update_status_label(self):
        self.status_label.config(
            text=f"Recursos disponibles: {self.available_resources}/{TOTAL_RECURSOS} - CPUs disponibles: {self.available_cpus}/{CPUS}"
        )

    def run_selected_scheduler(self):
        scheduler = self.scheduler_selection.get()
        if scheduler == "FIFO":
            self.run_fifo_simulation()
        elif scheduler == "SJF":
            self.run_sjf_simulation()
        elif scheduler == "Round Robin":
            self.run_rr_simulation()
        elif scheduler == "Priority":
            self.run_priority_simulation()

    def run_fifo_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para simular.")
            return

        self.processes.sort(key=lambda p: p.tiempo_llegada)
        self.simulate_fifo(0)

    def simulate_fifo(self, index):
        if index >= len(self.processes):
            detect_deadlock(self.processes)
            calculate_metrics(self.processes)
            messagebox.showinfo("Simulación", "La simulación ha terminado.")
            return

        process = self.processes[index]

        # Buscar su rectángulo y texto en el canvas
        for p, rect, text in self.canvas_processes:
            if p == process:
                break

        if recursos_global.asignar(process.recursos_necesarios) and self.available_cpus > 0:
            self.available_resources -= process.recursos_necesarios
            self.available_cpus -= 1
            self.update_status_label()

            process.set_estado("RUNNING")
            self.update_tree_status(process.pid, "RUNNING")
            self.canvas.itemconfig(rect, fill="green")

            self.root.after(
                process.tiempo_ejecucion * 1000,
                lambda: self.finish_process_fifo(process, rect, text, index)
            )
        else:
            process.set_estado("BLOCKED")
            self.update_tree_status(process.pid, "BLOCKED")
            self.canvas.itemconfig(rect, fill="red")
            self.root.after(2000, lambda: self.simulate_fifo(index + 1))

    def finish_process_fifo(self, process, rect, text, index):
        recursos_global.liberar(process.recursos_necesarios)
        self.available_resources += process.recursos_necesarios
        self.available_cpus += 1
        self.update_status_label()

        process.set_estado("FINISHED")
        self.update_tree_status(process.pid, "FINISHED")
        self.canvas.itemconfig(rect, fill="gray")
        self.root.after(1000, lambda: self.simulate_fifo(index + 1))


    def run_sjf_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para simular.")
            return

        # Ordenar procesos por tiempo restante
        self.processes.sort(key=lambda p: p.tiempo_restante)
        self.simulate_sjf(0)

    def simulate_sjf(self, index):
        if index >= len(self.processes):
            detect_deadlock(self.processes)
            calculate_metrics(self.processes)
            messagebox.showinfo("Simulación", "La simulación ha terminado.")
            return

        process = self.processes[index]

        for p, rect, text in self.canvas_processes:
            if p == process:
                break

        if recursos_global.asignar(process.recursos_necesarios):
            process.set_estado("RUNNING")
            self.update_tree_status(process.pid, "RUNNING")
            self.canvas.itemconfig(rect, fill="green")

            self.root.after(
                process.tiempo_ejecucion * 1000,
                lambda: self.finish_process_sjf(process, rect, text, index)
            )
        else:
            process.set_estado("BLOCKED")
            self.update_tree_status(process.pid, "BLOCKED")
            self.canvas.itemconfig(rect, fill="red")
            self.root.after(2000, lambda: self.simulate_sjf(index + 1))

    def finish_process_sjf(self, process, rect, text, index):
        recursos_global.liberar(process.recursos_necesarios)
        process.set_estado("FINISHED")
        self.update_tree_status(process.pid, "FINISHED")
        self.canvas.itemconfig(rect, fill="gray")
        self.simulate_sjf(index + 1)




    def run_rr_simulation(self):
        quantum = simpledialog.askinteger("Round Robin", "Ingrese el valor del quantum:")
        if quantum is None:
            return

        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para simular.")
            return

        self.simulate_rr(0, quantum)

    def simulate_rr(self, index, quantum):
        if not self.processes:
            detect_deadlock(self.processes)
            calculate_metrics(self.processes)
            messagebox.showinfo("Simulación", "La simulación ha terminado.")
            return

        process, rect, text = self.canvas_processes[index % len(self.processes)]

        if process.tiempo_restante == 0:
            index += 1
            self.simulate_rr(index, quantum)
            return

        if recursos_global.asignar(process.recursos_necesarios) and self.available_cpus > 0:
            self.available_resources -= process.recursos_necesarios
            self.available_cpus -= 1
            self.update_status_label()
            process.set_estado("RUNNING")
            self.update_tree_status(process.pid, "RUNNING")

            self.canvas.itemconfig(rect, fill="green")

            exec_time = min(quantum, process.tiempo_restante)
            process.tiempo_restante -= exec_time
            self.update_canvas_time_remaining(process.pid, process.tiempo_restante)

            self.root.after(exec_time * 1000, self.finish_rr_quantum, process, rect, text, index, quantum)
        else:
            process.set_estado("BLOCKED")
            self.update_tree_status(process.pid, "BLOCKED")
            self.canvas.itemconfig(rect, fill="red")
            self.root.after(2000, self.simulate_rr, index + 1, quantum)

    def finish_rr_quantum(self, process, rect, text, index, quantum):
        if process.tiempo_restante == 0:
            process.set_estado("TERMINATED")
            self.update_tree_status(process.pid, "TERMINATED")
            self.canvas.itemconfig(rect, fill="gray")
        else:
            process.set_estado("READY")
            self.update_tree_status(process.pid, "READY")
            self.canvas.itemconfig(rect, fill="blue")

        recursos_global.liberar(process.recursos_necesarios)
        self.available_resources += process.recursos_necesarios
        self.available_cpus += 1
        self.update_status_label()
        self.root.after(2000, self.simulate_rr, index + 1, quantum)

    def run_priority_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para simular.")
            return

        self.processes.sort(key=lambda p: p.prioridad)
        self.simulate_priority(0)

    def simulate_priority(self, index):
        if index >= len(self.processes):
            detect_deadlock(self.processes)
            calculate_metrics(self.processes)
            messagebox.showinfo("Simulación", "La simulación ha terminado.")
            return

        process = self.processes[index]

        for p, rect, text in self.canvas_processes:
            if p == process:
                break

        if recursos_global.asignar(process.recursos_necesarios):
            process.set_estado("RUNNING")
            self.update_tree_status(process.pid, "RUNNING")
            self.canvas.itemconfig(rect, fill="green")

            self.root.after(
                process.tiempo_ejecucion * 1000,
                lambda: self.finish_process_priority(process, rect, text, index)
            )
        else:
            process.set_estado("BLOCKED")
            self.update_tree_status(process.pid, "BLOCKED")
            self.canvas.itemconfig(rect, fill="red")
            self.root.after(2000, lambda: self.simulate_priority(index + 1))

    def finish_process_priority(self, process, rect, text, index):
        recursos_global.liberar(process.recursos_necesarios)
        process.set_estado("FINISHED")
        self.update_tree_status(process.pid, "FINISHED")
        self.canvas.itemconfig(rect, fill="gray")
        self.simulate_priority(index + 1)



    def finish_process(self, process, rect, text, index):
        process.set_estado("TERMINATED")
        self.update_tree_status(process.pid, "TERMINATED")

        self.canvas.itemconfig(rect, fill="gray")
        self.canvas.itemconfig(text, text=f"P{process.pid}\nDone")

        recursos_global.liberar(process.recursos_necesarios)
        self.update_status_label()

        self.root.after(1000, self.simulate_sjf if self.scheduler_selection.get() == "SJF" else self.simulate_priority, index + 1)


    def update_tree_status(self, pid, status):
        for item in self.tree.get_children():
            if int(self.tree.item(item, "values")[0]) == pid:
                values = list(self.tree.item(item, "values"))
                values[-2] = status  # Actualizar el estado
                self.tree.item(item, values=values)
                break

    def update_ui(self):
    # Actualiza la tabla y el canvas cada segundo
        for process in self.processes:
            if process.estado == "RUNNING" and process.tiempo_restante > 0:
                process.tiempo_restante -= 1
                self.update_tree_status(process.pid, process.estado)
                self.update_canvas_time_remaining(process.pid, process.tiempo_restante)

            if process.tiempo_restante == 0 and process.estado == "RUNNING":
                process.set_estado("TERMINATED")
                self.update_tree_status(process.pid, "TERMINATED")

        self.update_status_label()
        self.root.after(1000, self.update_ui)

    def update_canvas_time_remaining(self, pid, remaining_time):
        for process, rect, text in self.canvas_processes:
            if process.pid == pid:
                self.canvas.itemconfig(text, text=f"P{pid}\n{remaining_time}s")
                break

    def clear_entries(self):
        self.burst_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.resources_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessManagerApp(root)
    root.mainloop()
