from typing import cast

import injector
from domaindrivers.smartschedule.resource.employees.employee import Employee
from domaindrivers.smartschedule.resource.employees.employee_id import EmployeeId
from domaindrivers.smartschedule.resource.employees.employee_repository import EmployeeRepository
from domaindrivers.utils.optional import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session


class EmployeeRepositoryImpl(EmployeeRepository):  # type: ignore
    @injector.inject
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, employee: Employee) -> Employee:
        self.session.add(employee)
        self.session.commit()
        return employee

    def find_by_id(self, employee_id: EmployeeId) -> Optional[Employee]:
        return Optional(self.session.query(Employee).filter_by(_employee_id=employee_id.id()).first())

    def find_all_by_id(self, ids: list[EmployeeId]) -> list[Employee]:
        return cast(
            list[Employee],
            self.session.query(Employee).where(or_(*[Employee._id == employee_id for employee_id in ids])).all(),
        )

    def find_all(self) -> list[Employee]:
        return cast(list[Employee], self.session.query(Employee).all())

    def delete(self, employee: Employee) -> None:
        self.session.delete(employee)
        self.session.commit()
