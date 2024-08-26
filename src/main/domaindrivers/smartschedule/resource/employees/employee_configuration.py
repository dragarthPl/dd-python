import injector
from domaindrivers.smartschedule.resource.employees.employee_facade import EmployeeFacade
from domaindrivers.smartschedule.resource.employees.employee_repository import EmployeeRepository
from domaindrivers.smartschedule.resource.employees.employee_repository_impl import EmployeeRepositoryImpl
from injector import Module, provider, singleton


class EmployeeConfiguration(Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(EmployeeRepository, to=EmployeeRepositoryImpl)

    @singleton
    @provider
    def employee_facade(self, employee_repository: EmployeeRepository) -> EmployeeFacade:
        return EmployeeFacade(employee_repository)
