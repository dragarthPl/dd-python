from domaindrivers.smartschedule.planning.parallelization.stage import Stage
from domaindrivers.smartschedule.sorter.node import Node
from domaindrivers.smartschedule.sorter.nodes import Nodes


class StagesToNodes:
    def calculate(self, stages: list[Stage]) -> Nodes:
        result: dict[str, Node] = {stage.name: Node.from_name_stage(stage.name, stage) for stage in stages}

        for i, stage in enumerate(stages):
            result = self.__explicit_dependencies(stage, result)

        return Nodes(set(result.values()))

    def __explicit_dependencies(self, stage: Stage, result: dict[str, Node]) -> dict[str, Node]:
        node_with_explicit_deps: Node = result.get(stage.name)
        for explicit_dependency in stage.dependencies:
            node_with_explicit_deps = node_with_explicit_deps.depends_on(result.get(explicit_dependency.name))
        result[stage.name] = node_with_explicit_deps
        return result
