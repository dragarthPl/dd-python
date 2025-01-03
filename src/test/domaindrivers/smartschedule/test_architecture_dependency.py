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
            .layer("allocation")
            .containing_modules("domaindrivers.smartschedule.allocation")
            .layer("capabilityscheduling")
            .containing_modules("domaindrivers.smartschedule.allocation.capabilityscheduling")
            .layer("capabilityscheduling-acl")
            .containing_modules("domaindrivers.smartschedule.allocation.capabilityscheduling.legacyacl")
            .layer("cashflow")
            .containing_modules("domaindrivers.smartschedule.allocation.cashflow")
            .layer("parallelization")
            .containing_modules("domaindrivers.smartschedule.planning.parallelization")
            .layer("sorter")
            .containing_modules("domaindrivers.smartschedule.sorter")
            .layer("simulation")
            .containing_modules("domaindrivers.smartschedule.simulation")
            .layer("employee")
            .containing_modules("domaindrivers.smartschedule.resource.employees")
            .layer("device")
            .containing_modules("domaindrivers.smartschedule.resource.device")
            .layer("utils")
            .containing_modules("domaindrivers.utils")
            .layer("optimization")
            .containing_modules("domaindrivers.smartschedule.optimization")
            .layer("shared")
            .containing_modules("domaindrivers.smartschedule.shared")
            .layer("storage")
            .containing_modules("domaindrivers.storage")
        )

        rules = [
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("parallelization")
                .should_only()
                .access_layers_that()
                .are_named(
                    [
                        "sorter",
                        "utils",
                        "availability",
                    ]
                )
            ),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("availability")
                .should_only()
                .access_layers_that()
                .are_named(["shared", "utils"])
            ),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("allocation")
                .should_only()
                .access_layers_that()
                .are_named(
                    [
                        "shared",
                        "availability",
                        "cashflow",
                        "simulation",
                        "optimization",
                        "utils",
                        "storage",
                    ]
                )
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
                .are_named("employee")
                .should_only()
                .access_layers_that()
                .are_named(["capabilityscheduling", "shared", "utils", "storage"])
            ),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("device")
                .should_only()
                .access_layers_that()
                .are_named(["capabilityscheduling", "shared", "utils", "storage"])
            ),
            (
                LayerRule()
                .based_on(architecture)
                .layers_that()
                .are_named("capabilityscheduling-acl")
                .should_only()
                .access_layers_that()
                .are_named(["capabilityscheduling", "shared"])
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
