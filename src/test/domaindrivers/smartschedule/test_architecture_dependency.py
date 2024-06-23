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
            .layer("parallelization")
            .containing_modules("domaindrivers.smartschedule.planning.parallelization")
            .layer("sorter")
            .containing_modules("domaindrivers.smartschedule.sorter")
        )

        rules = [
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("parallelization")
                .should_only()
                .access_layers_that()
                .are_named("sorter")
            ),
            (LayerRule().based_on(architecture).layers_that().are_named("sorter").should_not().access_any_layer()),
        ]

        for rule in rules:
            rule.assert_applies(evaluable)
