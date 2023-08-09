def model1(graph):
    total_cpu = 0
    for i in graph.nodes:
        for j in i.children:
            for k in j.observations.series.data:
                print(k)
                total_cpu += k["cpu_load"]
        # # TODO remove assert - just for quick test
        # assert total_cpu == sum([0.34, 0.23, 0.11, 0.34, 0.23, 0.11])
    return total_cpu


def dow_msft_model(graph):
    """
    ref link: https://github.com/Green-Software-Foundation/sci-guide/blob/dev/use-case-submissions/dow-msft-Graph-DB.md

    E is energy in units kwH
    E calculated as:

    P[kwH] = (Pcpu + Pm or Pr + Power consumed by GPU or Pg Number of GPUs)/1000

    Pcpu = power consumed by CPU (or CPUs, in which case N cores * utilization)
    Pgpu = power consumed by GPU (or GPUs, in which case N units * utilization)
    Pmem = power consumed by memory

    RAM consumes 0.38kwh/GB, so 32GB allocated per VM equates to 32 * 0.38 = 12.16 kwh

    """
    TPU = 0
    E_cpu = []
    E_mem = []
    E_tot = []
    hours = 1
    RAM_consumption_per_gig = 0.38  # RAM consumes 0.38kwh/GB

    for i in graph.nodes:
        for j in i.children:
            # TODO make this a lookup to external file with server name as key
            TPU = get_TPU(j.observations.common.server)
            # calculate mean CPU load for each child
            cpu_loads = []
            for k in j.observations.series.data:
                cpu_loads.append(k["cpu_load"])
            cpu_load = 0
            for i in cpu_loads:
                cpu_load += i
            mean_cpu_load = cpu_load / len(cpu_loads)
            # append calculation of E for each child
            E_cpu.append(((TPU * mean_cpu_load) * hours) / 1000)

            # calculate Emem
            E_mem.append(
                ((j.observations.common.ram * RAM_consumption_per_gig) * hours) / 1000
            )
    total_E_cpu = sum(E_cpu)  # currently assumes data is given for one hour duration
    total_E_mem = sum(E_mem)

    for i in range(0, len(E_cpu)):
        E_tot.append(E_cpu[i] + E_mem[i])

    print(E_tot)
    return E_cpu, E_mem


def get_TPU(server):
    if server == "Intel-xeon-platinum-8380":
        return 270
    elif server == "Intel-xeon-platinum-8270":
        return 205
    else:
        return 200  # arbitrary default


# Ecpu = TDP * coefficient

# ((instance power consumption * data centre 'power usage effectiveness' * electricity carbon intensity) / 1000) + manufacturing emissions
# multiply by number of hours run for


# M = TE * (TR/EL) * (RR/TR)

# TE = Total Embodied Emissions - the sum of LCA emissions for all hardware components associated with the application server
# TR = Time Reserved, the length of time the hardware is reserved for use by the software.
# EL = Expected Lifespan, the anticipated time that the equipment will be installed.
# RR = Resources Reserved, the number of resources reserved for use by the software.
# TR = Total Resources, the total number of resources available.
