from typing import cast

import injector
from domaindrivers.smartschedule.resource.device.device import Device
from domaindrivers.smartschedule.resource.device.device_id import DeviceId
from domaindrivers.smartschedule.resource.device.device_repository import DeviceRepository
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session


class DeviceRepositoryImpl(DeviceRepository):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, device: Device) -> Device:
        self.session.add(device)
        self.session.commit()
        return device

    def find_by_id(self, device_id: DeviceId) -> Optional[Device]:
        return Optional(self.session.query(Device).filter_by(_device_id=device_id.id()).first())

    def find_all_by_id(self, ids: list[DeviceId]) -> list[Device]:
        return cast(
            list[Device],
            self.session.query(Device).where(or_(*[Device._id == device_id for device_id in ids])).all(),
        )

    def find_all(self) -> list[Device]:
        return cast(list[Device], self.session.query(Device).all())

    def delete(self, device: Device) -> None:
        self.session.delete(device)
        self.session.commit()
