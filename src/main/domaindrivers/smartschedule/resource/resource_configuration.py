import injector
from domaindrivers.smartschedule.resource.device.device_facade import DeviceFacade
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.resource_facade import ResourceFacade
from injector import Module, provider, singleton


class ResourceConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        pass

    @singleton
    @provider
    def device_facade(self, employee_facade: EmployeeFacade, device_facade: DeviceFacade) -> ResourceFacade:
        return ResourceFacade(employee_facade, device_facade)
