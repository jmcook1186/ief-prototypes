import yaml
from pathlib import Path
from models.models import dow_msft_model


class impact_graph:
    def __init__(self, impl):
        SRC_PATH = Path(__file__).resolve().parent
        input_file = SRC_PATH.joinpath("impls/" + impl).as_posix()
        with open(input_file, "r") as ymlfile:
            inputs = yaml.load(ymlfile, Loader=yaml.FullLoader)
        self.name = inputs["name"]
        self.description = inputs["description"]
        self.tags = dict(inputs["tags"])
        self.config = Config(inputs)
        self.graph = Graph(inputs["graph"])

    def run_model(self):
        if self.config.pipeline.calculation == "dow-msft":
            return dow_msft_model(self.graph)
        else:
            raise ValueError("Model not recognized")


class Graph:
    def __init__(self, inputs):
        nodes = []
        self.node_names = []
        self.nodes = []
        for i in inputs:
            node = Node(inputs[i])
            self.nodes.append(node)
            self.node_names.append(i)


class Node:
    def __init__(self, inputs):
        self.children = []
        for key in inputs:
            if key != "children":
                setattr(self, key, inputs[key])
        for childname in inputs["children"]:
            self.children.append(ChildNode(inputs["children"][childname], childname))


class ChildNode:
    def __init__(self, inputs, name):
        self.name = name
        self.observations = Observations(inputs["observations"])


class Observations:
    def __init__(self, inputs):
        for key in inputs:
            if key == "series":
                self.series = Series(inputs[key])
            else:
                setattr(self, key, inputs[key])


class Series:
    def __init__(self, inputs):
        self.timestamps = []
        for entry in inputs:
            for field in entry:
                # grab the time related data regardless of whether it is referred to
                # as 'datetime' or 'timestamp'
                if "time" in field:
                    self.timestamps.append(entry[field])
                else:
                    # this is weird syntax because we want to create arrays and append to them
                    # this is so we can create an attribute and append to them
                    if hasattr(self, field):
                        getattr(self, field).append(entry[field])
                    else:
                        setattr(self, field, [entry[field]])


class Config:
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
