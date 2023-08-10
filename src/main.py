from graph import impact_graph


graph = impact_graph()
graph2 = impact_graph()
# graph.show_name()
# graph.show_tags()
# graph.show_pipeline()
# graph.show_graph()
# print("***********")
# graph.show_data()
# print("\nCPU SUM = ", graph.run_model())


print(graph.graph.nodes[0].children[0].observations.common["server"])
print(graph.graph.nodes[0].children[0].observations.series.timestamps)
print(graph.graph.nodes[0].children[0].observations.series.cpu_load)


print(graph.graph.nodes[0].config["region"])
print(graph.graph.nodes[0].children[0].observations)
graph.run_model()
