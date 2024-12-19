import matplotlib.pyplot as plt

def calculate_metrics(processes):
    turnaround_times = []
    waiting_times = []
    response_times = []
    
    # Filtrar solo los procesos que han sido completados
    completed_processes = [p for p in processes if p.completion_time is not None]

    if not completed_processes:
        print("No hay procesos completados para calcular métricas.")
        return
    
    for i, process in enumerate(completed_processes):
        turnaround_time = process.completion_time - process.tiempo_llegada
        waiting_time = turnaround_time - process.tiempo_ejecucion
        
        
        if process.start_time is not None and process.tiempo_llegada is not None:
            response_time = process.start_time - process.tiempo_llegada
        else:
            response_time = 0  
        
        turnaround_times.append(turnaround_time)
        waiting_times.append(waiting_time)
        response_times.append(response_time)

        print(f"\nProceso {process.pid}:")
        print(f"Tiempo Requerido (Turnaround Time): {turnaround_time}")
        print(f"Tiempo de Espera (Waiting Time): {waiting_time}")
        print(f"Tiempo de Respuesta (Response Time): {response_time}")

    if len(turnaround_times) > 0:
        avg_turnaround = sum(turnaround_times) / len(turnaround_times)
    else:
        avg_turnaround = 0
    
    if len(waiting_times) > 0:
        avg_waiting = sum(waiting_times) / len(waiting_times)
    else:
        avg_waiting = 0

    if len(response_times) > 0:
        avg_response = sum(response_times) / len(response_times)
    else:
        avg_response = 0
    
    print("\n--- Métricas Promedio ---")
    print(f"Promedio de Tiempo Requerido (Turnaround Time): {avg_turnaround}")
    print(f"Promedio de Tiempo de Espera (Waiting Time): {avg_waiting}")
    print(f"Promedio de Tiempo de Respuesta (Response Time): {avg_response}")

    visualize_metrics(turnaround_times, waiting_times, response_times, completed_processes)
    draw_gantt_chart(completed_processes)


def visualize_metrics(turnaround_times, waiting_times, response_times, processes):
    labels = [f"P{process.pid}" for process in processes]
    fig, ax = plt.subplots()
    ax.plot(labels, turnaround_times, label="Tiempo Requerido", marker='o', color='blue', linestyle='-')
    ax.plot(labels, waiting_times, label="Tiempo de Espera", marker='o', color='red', linestyle='--')
    ax.plot(labels, response_times, label="Tiempo de Respuesta", marker='o', color='green', linestyle=':')

    ax.set_xlabel('Procesos(X)')
    ax.set_ylabel('Tiempo(Y)')
    ax.set_title('Gráfica Lineal - Planificación de Procesos')
    ax.legend()
    plt.show()

def draw_gantt_chart(processes):
    fig, gnt = plt.subplots()
    gnt.set_ylim(0, len(processes))
    gnt.set_xlim(0, max(p.completion_time for p in processes) + 1)

    gnt.set_yticks([i + 0.5 for i in range(len(processes))])
    gnt.set_yticklabels([f'Proceso {p.pid}' for p in processes])

    for i, process in enumerate(processes):
        start_time = process.start_time
        duration = process.tiempo_ejecucion
        gnt.broken_barh([(start_time, duration)], (i, 0.9), facecolors=('orange'))

    gnt.set_xlabel('Tiempo (x)')
    gnt.set_title('Diagrama de Gantt')
    plt.show()
