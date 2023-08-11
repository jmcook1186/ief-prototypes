import pandas as pd
import numpy as np
import warnings
from pathlib import Path


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
    data_path = SRC_PATH.joinpath("../data/aws-ec2-carbon-footprint.csv").as_posix()
    aws_data = pd.read_csv(data_path)

    RAM_consumption_per_gig = 0.38  # RAM consumes 0.38kwh/GB

    for i in graph.nodes:
        carbon_intensity = get_intensity(i.config["region"])
        for j in i.children:
            # TODO make this a lookup to external file with server name as key
            TPU = get_TPU(j.observations.common["server"])
            # calculate mean CPU load for each child
            cpu_loads = []
            for k in j.observations.series.cpu_load:
                cpu_loads.append(k)
            cpu_load = 0
            for i in cpu_loads:
                cpu_load += i
            mean_cpu_load = cpu_load / len(cpu_loads)
            # append calculation of E for each child
            E_cpu.append(((TPU * mean_cpu_load) * hours) / 1000)

            # calculate Emem
            E_mem.append(
                ((j.observations.common["ram"] * RAM_consumption_per_gig) * hours)
                / 1000
            )
            # calculate embodied C
            C_coeff = get_embodied_carbon_coefficient(j.observations.common["server"])
            lifespan = get_server_lifespan(j.observations.common["server"])
            instance_cpu = get_instance_cpu(j.observations.common["server"])
            instance_memory = get_instance_memory(
                j.observations.common["server"], aws_data
            )
            platform_cpu = get_platform_cpu(j.observations.common["server"])
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
    print("M_mem", M_mem)
    print("M_cpu", M_cpu)

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


def lookup_number(value, data, filter, target):
    """
    this function looks up numeric values in the aws dataframe
    it returns the value from the `target` column where the entry in the `filter` column matches `value`.
    If there is more than one value in the `filter` matching the given `value`, then the int(mean) of the retrieved values is returned.
    If `value` yields no valid values, the most common value in `target` is returned
    A warning is emitted in the latter case.
    """
    result = pd.to_numeric(data[data[filter] == value][target].values)
    if len(result) == 0 or result == None:
        # there are invalid entries in the original data that contain multiple commas separated values where there should be one int.
        # let's filter them out
        filtered_data = pd.to_numeric(
            data[target][data[target].str.contains(",") == False].values
        )
        # now we'll use the most common value as a stand in for our missing data
        vals, counts = np.unique(filtered_data, return_counts=True)
        warnings.warn(
            "{} not recognized, using most common value for {} from all {} in database".format(
                value, target, filter
            )
        )
        return vals[np.argmax(counts)]
    else:
        return int(result.mean())


def get_platform_memory(server, data):
    return lookup_number(server, data, "Platform CPU Name", "Platform Memory (in GB)")


def get_instance_cpu(server):
    # this data should be looked up from https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=504755275
    # in the EC2 isntances tab - the servers here are not actually listed, so let's return values from the Dow-msft github docs
    if server == "Intel-xeon-platinum-8380":
        return 1
    elif server == "Intel-xeon-platinum-8270":
        return 1
    else:
        return 1  # arbitrary default


def get_platform_cpu(server):
    # this data should be looked up from https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit#gid=504755275
    # in the EC2 isntances tab - the servers here are not actually listed, so let's return values from the Dow-msft github docs
    if server == "Intel-xeon-platinum-8380":
        return 8
    elif server == "Intel-xeon-platinum-8270":
        return 8
    else:
        return 8  # arbitrary default
