import argparse
from graph import impact_graph


# create a parser object
parser = argparse.ArgumentParser(description="ImpactYaml project")

# add argument
parser.add_argument(
    "--config", action="store_true", help="Prints out model configuration."
)
parser.add_argument(
    "--calculate",
    action="store_true",
    help="Runs model.",
)

# parse the arguments from standard input
args = parser.parse_args()
graph = impact_graph("dow_msft.yaml")

# # check if add argument has any input data.
# # If it has, then print sum of the given numbers
if args.config:
    graph.show_name()
    graph.show_tags()
    graph.show_pipeline()
    graph.show_graph()

    print("***********")
    graph.show_data()


if args.calculate:
    print("Total CPU usage = ", graph.run_model())
