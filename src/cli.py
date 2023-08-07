import argparse
from graph import impact_graph


# create a parser object
parser = argparse.ArgumentParser(description="ImpactYaml project")

# add argument
parser.add_argument(
    "-c", "--config", action="store_true", help="Prints out model configuration."
)

# parse the arguments from standard input
args = parser.parse_args()

# # check if add argument has any input data.
# # If it has, then print sum of the given numbers
if args.config:
    graph = impact_graph()
    graph.show_name()
    graph.show_tags()
    graph.show_pipeline()
    graph.show_graph()

    print("***********")
    graph.show_data()
