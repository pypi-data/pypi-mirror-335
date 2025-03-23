import networkx as nx
from matplotlib import pyplot as plt

from plurally.models.flow import Flow


def visuzalie_flow(flow: Flow, output: str = None):
    nx.draw(flow.graph)
    if output:
        plt.savefig(output)
    else:
        plt.show()


def main(): ...


if __name__ == "__main__":
    main()
