from typing import cast, Type

import injector
from domaindrivers.smartschedule.allocation.capabilityscheduling.capability_scheduler import CapabilityScheduler
from domaindrivers.smartschedule.resource.device.device_facade import DeviceFacade
from domaindrivers.smartschedule.resource.device.device_repository import DeviceRepository
from domaindrivers.smartschedule.resource.device.device_repository_sqlalchemy import DeviceRepositorySqlalchemy
from domaindrivers.smartschedule.resource.device.schedule_device_capabilities import ScheduleDeviceCapabilities
from injector import Module, provider, singleton


class DeviceConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(cast(Type[DeviceRepository], DeviceRepository), to=DeviceRepositorySqlalchemy)

    @singleton
    @provider
    def device_facade(
        self, device_repository: DeviceRepository, capability_scheduler: CapabilityScheduler
    ) -> DeviceFacade:
        return DeviceFacade(device_repository, ScheduleDeviceCapabilities(device_repository, capability_scheduler))
