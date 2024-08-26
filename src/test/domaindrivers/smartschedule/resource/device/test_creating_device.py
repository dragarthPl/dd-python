from test.domaindrivers.smartschedule.dependency_resolver import DependencyResolverForTest
from test.domaindrivers.smartschedule.test_db_configuration import TestDbConfiguration
from unittest import TestCase

from domaindrivers.smartschedule.resource.device.device_facade import DeviceFacade
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.resource.device.device_summary import DeviceSummary
from domaindrivers.smartschedule.shared.capability.capability import Capability


class TestCreatingDevice(TestCase):
    SQL_SCRIPTS: tuple[str] = ("schema-resources.sql",)
    test_db_configuration: TestDbConfiguration = TestDbConfiguration(scripts=SQL_SCRIPTS)

    device_facade: DeviceFacade

    def setUp(self) -> None:
        dependency_resolver = DependencyResolverForTest(self.test_db_configuration.data_source().connection_url)
        self.device_facade = dependency_resolver.resolve_dependency(DeviceFacade)

    def test_can_create_and_load_devices(self) -> None:
        # given
        device: DeviceId = self.device_facade.create_device(
            "super-excavator-1000", Capability.assets("BULLDOZER", "EXCAVATOR")
        )

        # when
        loaded: DeviceSummary = self.device_facade.find_device(device)

        # then
        self.assertEqual(loaded.assets, Capability.assets("BULLDOZER", "EXCAVATOR"))
        self.assertEqual("super-excavator-1000", loaded.model)

    def test_can_find_all_capabilities(self) -> None:
        # given
        self.device_facade.create_device("super-excavator-1000", Capability.assets("SMALL-EXCAVATOR", "BULLDOZER"))
        self.device_facade.create_device(
            "super-excavator-2000", Capability.assets("MEDIUM-EXCAVATOR", "UBER-BULLDOZER")
        )
        self.device_facade.create_device("super-excavator-3000", Capability.assets("BIG-EXCAVATOR"))

        # when
        loaded: list[Capability] = self.device_facade.find_all_capabilities()

        # then
        for asset in (
            Capability.asset("SMALL-EXCAVATOR"),
            Capability.asset("BULLDOZER"),
            Capability.asset("MEDIUM-EXCAVATOR"),
            Capability.asset("UBER-BULLDOZER"),
            Capability.asset("BIG-EXCAVATOR"),
        ):
            self.assertIn(asset, loaded)
