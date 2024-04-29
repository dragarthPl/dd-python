from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.sorter.node import Node
from domaindrivers.smartschedule.sorter.nodes import Nodes


class StagesToNodes:
    def calculate(self, stages: list[Stage]) -> Nodes:
        result: dict[str, Node] = {stage.name: Node.from_name_stage(stage.name, stage) for stage in stages}

        for i, stage in enumerate(stages):
            result = self.__explicit_dependencies(stage, result)
            result = self.__shared_resources(stage, stages[i + 1 :], result)

        return Nodes(set(result.values()))

    def __shared_resources(self, stage: Stage, with_stages: list[Stage], result: dict[str, Node]) -> dict[str, Node]:
        for other in with_stages:
            if not stage.name == other.name:
                if not stage.resources.isdisjoint(other.resources):
                    node: Node
                    if len(other.resources) > len(stage.resources):
                        node = result.get(stage.name)
                        node = node.depends_on(result.get(other.name))
                        result[stage.name] = node
                    else:
                        node = result.get(other.name)
                        node = node.depends_on(result.get(stage.name))
                        result[other.name] = node
        return result

    def __explicit_dependencies(self, stage: Stage, result: dict[str, Node]) -> dict[str, Node]:
        node_with_explicit_deps: Node = result.get(stage.name)
        for explicit_dependency in stage.dependencies:
            node_with_explicit_deps = node_with_explicit_deps.depends_on(result.get(explicit_dependency.name))
        result[stage.name] = node_with_explicit_deps
        return result
