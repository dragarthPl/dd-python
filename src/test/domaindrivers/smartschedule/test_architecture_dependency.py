import os
from pathlib import Path
from unittest import TestCase

from pytestarch import get_evaluable_architecture, LayeredArchitecture, LayerRule  # type: ignore[attr-defined]

ROOT_DIR = os.path.join(
    str(Path(os.path.join(os.path.abspath(__file__))).parent.parent.parent.parent), "main", "domaindrivers"
)
MODULE_DIR = os.path.join(
    str(Path(os.path.join(os.path.abspath(__file__))).parent.parent.parent.parent), "main", "domaindrivers"
)


class ArchitectureDependencyTest(TestCase):
    def test_check_dependencies(self) -> None:
        evaluable = get_evaluable_architecture(str(ROOT_DIR), str(MODULE_DIR))

        architecture = (
            LayeredArchitecture()  # type: ignore[attr-defined]
            .layer("availability")
            .containing_modules("domaindrivers.smartschedule.availability")
            .layer("parallelization")
            .containing_modules("domaindrivers.smartschedule.planning.parallelization")
            .layer("sorter")
            .containing_modules("domaindrivers.smartschedule.sorter")
            .layer("simulation")
            .containing_modules("domaindrivers.smartschedule.simulation")
            .layer("utils")
            .containing_modules("domaindrivers.utils")
            .layer("optimization")
            .containing_modules("domaindrivers.smartschedule.optimization")
            .layer("shared")
            .containing_modules("domaindrivers.smartschedule.shared")
        )

        rules = [
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("parallelization")
                .should_only()
                .access_layers_that()
                .are_named(["sorter", "shared", "utils"])
            ),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("availability")
                .should_only()
                .access_layers_that()
                .are_named(["shared"])
            ),
            (LayerRule().based_on(architecture).layers_that().are_named("sorter").should_not().access_any_layer()),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("simulation")
                .should_only()
                .access_layers_that()
                .are_named(["utils", "optimization", "shared"])
            ),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("shared")
                .should_only()
                .access_layers_that()
                .are_named(["utils"])
            ),
        ]

        for rule in rules:
            rule.assert_applies(evaluable)
