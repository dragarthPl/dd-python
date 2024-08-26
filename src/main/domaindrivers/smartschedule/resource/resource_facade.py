from typing import Final

from domaindrivers.smartschedule.resource.device.device_facade import DeviceFacade
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.shared.capability.capability import Capability


class ResourceFacade:
    __employee_facade: Final[EmployeeFacade]
    __device_facade: Final[DeviceFacade]

    def __init__(self, employee_facade: EmployeeFacade, device_facade: DeviceFacade) -> None:
        self.__employee_facade = employee_facade
        self.__device_facade = device_facade

    def find_all_capabilities(self) -> list[Capability]:
        employee_capabilities: list[Capability] = self.__employee_facade.find_all_capabilities()
        device_capabilities: list[Capability] = self.__device_facade.find_all_capabilities()
        return list(employee_capabilities + device_capabilities)
