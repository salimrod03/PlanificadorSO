import time
from Graficas import calculate_metrics

def fifo_scheduling(processes, recursos):
    current_time = 0
    completed_processes = []  # Para almacenar los procesos completados

    for process in processes:
        if recursos.asignar(process.recursos_necesarios):
            process.set_estado("RUNNING")
            process.start_time = current_time
            print(f"\nEjecutando proceso {process.pid}. \nEstado: {process.estado}. \nTiempo actual: {current_time}")

            time.sleep(2)  # Pausa de 2 segundos para simular ejecución
            current_time += process.tiempo_ejecucion
            
            process.completion_time = current_time
            process.set_estado("TERMINATED")
            recursos.liberar(process.recursos_necesarios)
            print(f"\nProceso {process.pid} completado. \nEstado: {process.estado}. \nTiempo actual: {current_time}")
            print("==================================================== \n")
            completed_processes.append(process)  
        else:
            process.set_estado("BLOCKED")
            print(f"Proceso {process.pid} no puede iniciarse, recursos insuficientes.")
            time.sleep(2)  

    if completed_processes:
        calculate_metrics(completed_processes)
    else:
        print("No hay procesos completados para calcular métricas.")

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
