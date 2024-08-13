import uuid

from attr import frozen


@frozen
class ResourceAvailabilityId:
    resource_availability_id: uuid.UUID

    @classmethod
    def none(cls) -> "ResourceAvailabilityId":
        return cls(None)

    @classmethod
    def new_one(cls) -> "ResourceAvailabilityId":
        return cls(uuid.uuid4())

    @classmethod
    def of(cls, resource_availability_id: uuid.UUID) -> "ResourceAvailabilityId":
        if resource_availability_id is None:
            return cls.none()
        return ResourceAvailabilityId(resource_availability_id)
