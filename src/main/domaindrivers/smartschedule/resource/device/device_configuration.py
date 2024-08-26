from typing import cast, Type

import injector
from domaindrivers.smartschedule.resource.device.device_facade import DeviceFacade
from domaindrivers.smartschedule.resource.device.device_repository import DeviceRepository
from domaindrivers.smartschedule.resource.device.device_repository_sqlalchemy import DeviceRepositorySqlalchemy
from injector import Module, provider, singleton


class DeviceConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(cast(Type[DeviceRepository], DeviceRepository), to=DeviceRepositorySqlalchemy)

    @singleton
    @provider
    def device_facade(self, device_repository: DeviceRepository) -> DeviceFacade:
        return DeviceFacade(device_repository)
