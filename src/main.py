from graph import impact_graph


graph = impact_graph()
graph.show_name()
graph.show_tags()
graph.show_pipeline()
graph.show_graph()

print("***********")
graph.show_data()


print("\nCPU SUM = ", graph.calculate_cpu_sum())
