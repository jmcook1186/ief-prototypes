def model1(graph):
    total_cpu = 0
    for i in graph.nodes:
        for j in i.children:
            for k in j.observations.series.data:
                total_cpu += k["cpu"]
        # TODO remove assert - just for quick test
        assert total_cpu == sum([0.34, 0.23, 0.11, 0.34, 0.23, 0.11])
    return total_cpu
