import pandas as pd
from pathlib import Path
from utils import lookup_number


def dow_msft_model(graph):
    """
    ref link: https://github.com/Green-Software-Foundation/sci-guide/blob/dev/use-case-submissions/dow-msft-Graph-DB.md
    """
    TPU = 0
    E_cpu = []
    E_mem = []
    E_tot = []
    E_tot_C = []
    M_cpu = []
    M_mem = []
    M_tot = []
    hours = 1
    SRC_PATH = Path(__file__).resolve().parent
    aws_data_path = SRC_PATH.joinpath("../data/aws-ec2-carbon-footprint.csv").as_posix()
    aws_data = pd.read_csv(aws_data_path)
    # RAM consumes 0.38kwh/GB,
    # https://www.crucial.com/support/articles-faq-memory/how-much-power-does-memory-use
    RAM_consumption_per_gig = 0.38

    for i in graph.nodes:
        carbon_intensity = get_intensity(i.config["region"])
        for j in i.children:
            # TODO make this a lookup to external file with server name as key
            # Where can this data come from?
            TPU = get_TPU(j.observations.common["server"])
            mean_tdp_coeff = time_normalization(j.observations.series.tdp_coeff)
            # append calculation of E for each child
            E_cpu.append(((TPU * mean_tdp_coeff) * hours) / 1000)

            # calculate Emem for each child

            mean_mem = time_normalization(j.observations.series.memory_utilization)

            E_mem.append(((mean_mem * RAM_consumption_per_gig) * hours) / 1000)
            # calculate embodied C
            C_coeff = get_embodied_carbon_coefficient(j.observations.common["server"])
            lifespan = get_server_lifespan(j.observations.common["server"])
            instance_cpu = get_instance_cpu(j.observations.common["server"], aws_data)
            instance_memory = get_instance_memory(
                j.observations.common["server"], aws_data
            )
            platform_cpu = get_platform_cpu(j.observations.common["server"], aws_data)
            platform_memory = get_platform_memory(
                j.observations.common["server"], aws_data
            )
            M_cpu.append(C_coeff * (hours / lifespan) * (instance_cpu / platform_cpu))
            M_mem.append(
                C_coeff * (hours / lifespan) * (instance_memory / platform_memory)
            )

    total_E_cpu = sum(E_cpu)  # currently assumes data is given for one hour duration
    total_E_mem = sum(E_mem)
    total_M_cpu = sum(M_cpu)
    total_M_mem = sum(M_mem)

    for i in range(0, len(E_cpu)):
        E_tot.append(E_cpu[i] + E_mem[i])
        E_tot_C.append(E_cpu[i] * carbon_intensity + E_mem[i] * carbon_intensity)
    for i in range(0, len(M_cpu)):
        M_tot.append(M_cpu[i] + M_mem[i])

    print("total embodied = ", sum(M_tot) * 1000)
    print("total energy in kwh = ", sum(E_tot))
    print("total carbon from CPU = ", sum(E_tot_C))
    print("total carbon = ", (sum(E_tot_C) + sum(M_tot) * 1000))
    return E_tot


def get_intensity(region):
    if region == "east-us":
        return 554
    else:
        return 500  # arbitrary default


def get_TPU(server):
    if server == "Intel-xeon-platinum-8380":
        return 270
    elif server == "Intel-xeon-platinum-8270":
        return 205
    else:
        return 200  # arbitrary default


def get_embodied_carbon_coefficient(server):
    if server == "Intel-xeon-platinum-8380":
        return 1533.12
    elif server == "Intel-xeon-platinum-8270":
        return 1216.62
    else:
        return 1400  # arbitrary default


def get_server_lifespan(server):
    # returns lifespan in hours (n yr * 365 * 24)
    if server == "Intel-xeon-platinum-8380":
        return 4 * 365 * 24
    elif server == "Intel-xeon-platinum-8270":
        return 4 * 365 * 24
    else:
        return 4 * 365 * 24  # arbitrary default


def get_instance_memory(server, data):
    return lookup_number(server, data, "Platform CPU Name", "Instance Memory (in GB)")


def get_platform_memory(server, data):
    return lookup_number(server, data, "Platform CPU Name", "Platform Memory (in GB)")


def get_instance_cpu(server, data):
    return lookup_number(server, data, "Platform CPU Name", "Instance vCPU")


def get_platform_cpu(server, data):
    return lookup_number(
        server, data, "Platform CPU Name", "Platform Total Number of vCPU"
    )


def time_normalization(in_data):
    """
    calculate mean CPU energy for each child
    taking the mean is a stand-in for a proper time normalization - coming soon
    """
    temp_data = []
    for k in in_data:
        temp_data.append(k)
    temp = 0
    for i in temp_data:
        temp += i
    out_data = temp / len(temp_data)

    return out_data
