import time
from Graficas import calculate_metrics

def round_robin_scheduling(processes, quantum, recursos):
    current_time = 0
    queue = processes[:]  
    blocked_attempts = {p.pid: 0 for p in processes}  # Intentos fallidos por proceso
    MAX_BLOCKED_ATTEMPTS = 3  

    while queue:
        for process in queue:
            if recursos.asignar(process.recursos_necesarios):  
                recursos.liberar(process.recursos_necesarios)  # Al finalizar, se liberan los mismos recursos
                blocked_attempts[process.pid] = 0  # Reinicia el contador de intentos fallidos
                if process.tiempo_restante == process.tiempo_ejecucion:
                    process.set_estado("RUNNING")
                    process.start_time = current_time

                exec_time = min(quantum, process.tiempo_restante)
                print(f"\nEjecutando proceso {process.pid}. \nEstado: {process.estado}. \nTiempo actual: {current_time}")
                time.sleep(2)  
                current_time += exec_time 
                process.tiempo_restante -= exec_time
                
                if process.tiempo_restante == 0:
                    process.completion_time = current_time
                    process.set_estado("TERMINATED")
                    recursos.liberar(1)
                    print(f"\nProceso {process.pid} completado. \nEstado: {process.estado}. \nTiempo actual: {current_time}")
                    print("==================================================== \n")
                    time.sleep(2) 
                    queue.remove(process)
                else:
                    print(f"Proceso {process.pid} no ha terminado. \nEstado: {process.estado}. \nTiempo restante: {process.tiempo_restante}")
                    time.sleep(2)  
                    recursos.liberar(1)
            else:
                process.set_estado("BLOCKED")
                blocked_attempts[process.pid] += 1
                print(f"Proceso {process.pid} no puede continuar, recursos insuficientes. Intento {blocked_attempts[process.pid]}")
                time.sleep(2) 
                
                # Si ha fallado en asignar recursos varias veces, lo evacuamos
                if blocked_attempts[process.pid] >= MAX_BLOCKED_ATTEMPTS:
                    process.set_estado("EVACUATED")
                    print(f"Proceso {process.pid} 'EVACUATED' por falta de recursos tras {MAX_BLOCKED_ATTEMPTS} intentos.")
                    time.sleep(2)  
                    queue.remove(process)
    
    detect_deadlock(processes)
    calculate_metrics(processes)

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
