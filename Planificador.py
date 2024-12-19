import time
from Graficas import calculate_metrics
from FIFO import fifo_scheduling
from Priority import priority_scheduling
from RR import round_robin_scheduling
from SJF import sjf_scheduling
from Procesos import Process
from Recursos import Recurso

def run_simulation(processes, recurso, cpus, choice, quantum=None):
    print("\n============= Planificador de Procesos ============= ")

    # Valida si hay procesos
    if not processes:
        raise ValueError("No hay procesos para simular.")

    # Lógica del planificador según la elección
    if choice == 1:
        print("\n------- Ejecución FIFO -------")
        fifo_scheduling(processes, recurso)
        print("\n------------------------------")
    elif choice == 2:
        print("\n------- Ejecución SJF -------")
        sjf_scheduling(processes, recurso)
        print("\n-----------------------------")
    elif choice == 3:
        if quantum is None:
            raise ValueError("Se requiere un valor de quantum para el planificador Round Robin.")
        print("\n------- Ejecución Round Robin -------")
        round_robin_scheduling(processes, quantum, recurso)
        print("\n-------------------------------------")
    elif choice == 4:
        print("\n------- Ejecución Prioridad -------")
        priority_scheduling(processes, recurso)
        print("\n------------------------------------")
    else:
        raise ValueError("Opción no válida.")
    
if __name__ == "__main__":
    run_simulation()
