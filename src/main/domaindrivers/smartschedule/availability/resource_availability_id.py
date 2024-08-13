import uuid

from attr import frozen
from domaindrivers.storage.uuid_pg import UUID


@frozen
class ResourceAvailabilityId:
    resource_availability_id: UUID

    @classmethod
    def none(cls) -> "ResourceAvailabilityId":
        return ResourceAvailabilityId(None)

    @classmethod
    def new_one(cls) -> "ResourceAvailabilityId":
        return ResourceAvailabilityId(uuid.uuid4())

    @classmethod
    def of(cls, resource_availability_id: UUID) -> "ResourceAvailabilityId":
        if resource_availability_id is None:
            return cls.none()
        return ResourceAvailabilityId(resource_availability_id)
