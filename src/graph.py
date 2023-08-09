import yaml
from pathlib import Path
from models.models import dow_msft_model


class impact_graph:
    """
    The impact graph is a class representing the mpact.yaml.
    It is the highest level object in the project. The information
    in impact.yaml is marshalled into into appropriate types and
    assigned to class attributes. Then, class method can operate on
    the information. This is how the impact.yaml becomes executable.

    Inputs:
    - None

    Attributes:
    - name
    - description
    - tags
    - config
    - graph

    Methods:
    -
    """

    def __init__(self):
        SRC_PATH = Path(__file__).resolve().parent
        input_file = SRC_PATH.joinpath("dow_msft_graph.yaml").as_posix()
        print(input_file)
        with open(input_file, "r") as ymlfile:
            inputs = yaml.load(ymlfile, Loader=yaml.FullLoader)
        print(inputs)
        self.name = inputs["name"]
        self.description = inputs["description"]
        self.tags = dict(inputs["tags"])
        self.config = GraphConfig(inputs)
        self.graph = Graph(inputs)

    def show_name(self):
        print("\nName", "\n----\n", self.name)

    def show_tags(self):
        print("\nTags", "\n----\n")
        for i in self.tags:
            print(i, ": ", self.tags[i])

    def show_pipeline(self):
        print("\nPipeline", "\n--------\n")
        for i in vars(self.config.pipeline):
            print(i, ": ", getattr(self.config.pipeline, i))

    def show_graph(self):
        print("\nGraph", "\n-----\n")
        for i in self.graph.node_names:
            print("Nodes: ", i)

    def show_data(self):
        for i in self.graph.nodes:
            for j in i.children:
                print("Child: ", j.type, j.id, "\n")
                print(j.observations.series.data)

    def run_model(self):
        if self.config.pipeline.calculation == "dow-msft":
            return dow_msft_model(self.graph)
        else:
            raise ValueError("Model not recognized")


class GraphConfig:
    def __init__(self, inputs):
        calculation = inputs["config"]["pipeline"]["calculation"]
        normalization = inputs["config"]["pipeline"]["normalization"]
        aggregation = inputs["config"]["pipeline"]["aggregation"]
        self.pipeline = Pipeline(calculation, normalization, aggregation)


class Pipeline:
    def __init__(self, calculation, normalization, aggregation):
        self.calculation = calculation
        self.normalization = normalization
        self.aggregation = aggregation


class Graph:
    def __init__(self, inputs):
        node_names = []
        nodes = []
        for i in inputs["graph"]:
            node_names.append(i)
            nodes.append(Node(inputs["graph"][i]))
        self.node_names = node_names
        self.nodes = nodes


class Node:
    def __init__(self, inputs):
        self.model = inputs["model"]
        self.config = NodeConfig(inputs["config"])
        children = []
        child_names = []
        for n, i in enumerate(inputs["children"]):
            child_names.append(i)
            children.append(Child(i, n, inputs["children"][i]))
        self.child_names = child_names
        self.children = children


class NodeConfig:
    def __init__(self, inputs):
        self.vendor = inputs["vendor"]
        self.region = inputs["region"]


class Child:
    def __init__(self, name, id, inputs):
        if name == "queue":
            self.id = id
            self.type = "queue"
            self.observations = Observation(inputs["observations"])

        elif name == "servers":
            self.type = "server"
            self.id = id
            # self.config =
            # self.params =
            self.observations = Observation(inputs["observations"])

        elif name == "database":
            self.type = "database"
            self.id = id
            # self.config =
            # self.params =
            self.observations = Observation(inputs["observations"])

        elif name == "api":
            self.type = "api"
            self.id = id
            # self.config =
            # self.params =
            self.observations = Observation(inputs["observations"])


class Observation:
    def __init__(self, inputs):
        self.common = Common(inputs)
        self.series = Series(inputs["series"])


class Common:
    def __init__(self, inputs):
        try:
            self.sku = inputs["common"]["sku"]
        except:
            self.sku = None
        self.n_cpu = inputs["common"]["n_cpu"]
        self.ram = inputs["common"]["ram"]
        self.server = inputs["common"]["server"]


class Series:
    def __init__(self, inputs):
        self.data = inputs
