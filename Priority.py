import time
from Graficas import calculate_metrics

def priority_scheduling(processes, recursos):
    current_time = 0
    processes.sort(key=lambda p: p.prioridad)
    blocked_attempts = {p.pid: 0 for p in processes}
    MAX_BLOCKED_ATTEMPTS = 3

    for process in processes:
        if recursos.asignar(process.recursos_necesarios):
            blocked_attempts[process.pid] = 0
            process.set_estado("RUNNING")
            process.start_time = current_time
            print(f"\nEjecutando proceso {process.pid}. \nEstado: {process.estado}. \nTiempo actual: {current_time}")
            
            time.sleep(2)
            current_time += process.tiempo_ejecucion
            process.completion_time = current_time
            process.set_estado("TERMINATED")
            recursos.liberar(process.recursos_necesarios)
            print(f"\nProceso {process.pid} completado. \nEstado: {process.estado}. \nTiempo actual: {current_time}")
            print("==================================================== \n")
        else:
            process.set_estado("BLOCKED")
            blocked_attempts[process.pid] += 1
            print(f"Proceso {process.pid} no puede iniciar, recursos insuficientes. Intento {blocked_attempts[process.pid]}")
            time.sleep(2)
            
            if blocked_attempts[process.pid] >= MAX_BLOCKED_ATTEMPTS:
                process.set_estado("EVACUATED")
                print(f"Proceso {process.pid} 'EVACUATED' por falta de recursos tras {MAX_BLOCKED_ATTEMPTS} intentos.")
                time.sleep(2)
    
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
