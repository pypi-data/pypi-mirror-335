import psutil

def get_free_cpus(threshold=10):
    cpu_usages = psutil.cpu_percent(interval=1,percpu=True)
    free_cpus = [i for i,usage in enumerate(cpu_usages) if usage < threshold]
    if len(free_cpus)  == 0:
        return [0]
    else:
        return free_cpus