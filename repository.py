'''repository.py'''

from typing import List, Optional
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist
from schemas import EmployeeAdd, EmployeeUpdate, Subdivision, VacationAdd
from schemas import VacationUpdate
from models import Employees, Subdivisions, Vacations

class Repository(BaseModel):
    '''Класс функций для роутера'''
    @classmethod
    async def get_all_employees(cls):
        '''Функция для получения списка всех работников'''
        return await Employees.all()
    
    @classmethod
    async def get_employee_by_id(cls, user_id: int):
        '''Функция для получения работника по ID'''
        return await Employees.get_or_none(id=user_id)

    @classmethod
    async def get_employee(
        cls,
        last_name: Optional[str] = None,
        first_name: Optional[str] = None,
        patronymic: Optional[str] = None,
        email: Optional[str] = None,
        login: Optional[str] = None,
    ) -> List[Employees]:
        '''Функция для получения работника'''
        query = Employees.all()

        if last_name:
            query = query.filter(last_name__iexact=last_name)
        if first_name:
            query = query.filter(first_name__iexact=first_name)
        if patronymic:
            query = query.filter(patronymic__iexact=patronymic)
        if email:
            query = query.filter(email__iexact=email)
        if login:
            query = query.filter(login__iexact=login)
        return await query

    @classmethod
    async def add_employee(cls,employee: EmployeeAdd) -> Employees:
        '''Функция для добавления работника'''
        employee = await Employees.create(**employee.model_dump())
        return employee

    @classmethod
    async def update_employee(cls, id: int, employee: EmployeeUpdate) -> Optional[Employees]:
        '''Функция для обновления работника'''
        emp = await Employees.get_or_none(id=id)
        if emp:
            await emp.update_from_dict(employee.model_dump(exclude_none=True))
            await emp.save()
            return emp
        return emp

    @classmethod
    async def delete_employee(cls,id: int) -> bool:
        '''Функция для удаления работника'''
        emp = await Employees.get_or_none(id=id)
        if emp:
            await emp.delete()
            return emp
        return emp

    @classmethod
    async def get_all_subdivisions(cls):
        '''Функция для получения всех подразделений'''
        subdivisions = await Subdivisions.all().prefetch_related('employees', 'leader')
        result = []
        for subdivision in subdivisions:
            employee_ids = [employee.id for employee in subdivision.employees]
            result.append({
                'id': subdivision.id,
                'name': subdivision.name,
                'leader_id': subdivision.leader.id if subdivision.leader else None,
                'employee_ids': employee_ids,
            })
        return result

    @classmethod
    async def get_subdivision_by_id(cls, subdivision_id: int) -> Optional[Subdivisions]:
        '''Функция для получения подразделения по айди'''
        subdivision = await Subdivisions.filter(id=subdivision_id).prefetch_related('employees').first()
        if subdivision:
            subdivision.employee_ids = [employee.id for employee in subdivision.employees]
        return subdivision

    @classmethod
    async def add_subdivision(cls, name: str, leader_id: Optional[int] = None) -> Optional[Subdivisions]:
        '''Функция для добавления подразделения'''
        try:
            leader = await Employees.get(id=leader_id) if leader_id else None
        except DoesNotExist:
            return None

        new_subdivision = await Subdivisions.create(name=name, leader=leader)
        return new_subdivision

    @classmethod
    async def update_subdivision(cls, subdivision_id: int, name: str) -> Optional[Subdivisions]:
        '''Функция для обновления подразделения'''
        sub = await Subdivisions.get_or_none(id=subdivision_id)
        if sub is None:
            return None
        sub.name = name.lower()
        await sub.save()
        return sub

    @classmethod
    async def assign_leader(cls, subdivision_id: int, leader_id: int) -> Optional[Subdivisions]:
        '''Функция для добавления руководителя к подразделению'''
        try:
            subdivision = await Subdivisions.get(id=subdivision_id)
            leader = await Employees.get(id=leader_id)
        except DoesNotExist:
            return None

        subdivision.leader = leader
        await subdivision.save()
        return subdivision

    @classmethod
    async def assign_employee_to_subdivision(cls, subdivision_id: int, employee_id: int) -> Optional[Subdivisions]:
        '''Функция для прикреплению работника к подразделению'''
        subdivision = await Subdivisions.get_or_none(id=subdivision_id)
        if not subdivision:
            return None

        employee = await Employees.get_or_none(id=employee_id)
        if not employee:
            return None
        await subdivision.employees.add(employee)
        return subdivision

    @classmethod
    async def remove_employee_from_subdivision(cls, subdivision_id: int, employee_id: int) -> Optional[Subdivision]:
        '''Функция для открепления работника от подразделения'''
        subdivision = await Subdivisions.get_or_none(id=subdivision_id)
        if not subdivision:
            return None
        employee = await Employees.get_or_none(id=employee_id)
        if not employee:
            return None
        await subdivision.employees.remove(employee)
        await subdivision.fetch_related('employees')
        subdivision_data = Subdivision(
            id=subdivision.id,
            name=subdivision.name,
            leader_id=subdivision.leader_id,
            employee_ids=[employee.id for employee in subdivision.employees]
        )
        return subdivision_data

    @classmethod
    async def delete_subdivision(cls, id: int) -> bool:
        '''Функция для удаления подразделения'''
        sub = await Subdivisions.get_or_none(id=id)
        if sub:
            await sub.delete()
            return sub
        return sub

    @classmethod
    async def get_all_vacations(cls):
        '''Функция для получения всех отпусков и командировок'''
        return await Vacations.all()

    @classmethod
    async def get_employee_with_vacations(cls, employee_id: Optional[int] = None,
                                          type: Optional[str] = None):
        '''Функция для получения работника с отпусками или командировками'''
        filters = {}
        if employee_id:
            filters["id"] = employee_id
        employees = await Employees.filter(**filters).prefetch_related('vacations')
        result = []
        for employee in employees:
            vacations = employee.vacations
            if type:
                vacations = [vacation for vacation in vacations if vacation.type == type]
            result.append({
                "id": employee.id,
                "last_name": employee.last_name,
                "first_name": employee.first_name,
                "patronymic": employee.patronymic,
                "email": employee.email,
                "login": employee.login,
                "password": employee.password,
                "vacations": [
                    {
                        "id": vacation.id,
                        "employee_id": employee.id,
                        "start_date": vacation.start_date,
                        "end_date": vacation.end_date,
                        "type": vacation.type
                    }
                    for vacation in vacations
                ]
            })
        return result

    @classmethod
    async def add_vacation(cls, vacation: VacationAdd) -> Optional[Vacations]:
        '''Функция для добавления отпуска или командировки'''
        overlaps = await Vacations.filter(
            employee_id=vacation.employee_id,
            start_date__lte=vacation.end_date,
            end_date__gte=vacation.start_date
        ).exists()
        if overlaps:
            return None
        new_vacation = await Vacations.create(**vacation.model_dump())
        return new_vacation

    @classmethod
    async def update_vacation(cls, id: int, vacation: VacationUpdate) -> Optional[Vacations]:
        '''Функция для обновления отпуска или командировки'''
        overlap = await Vacations.filter(
            start_date__lt=vacation.end_date,
            end_date__gt=vacation.start_date
        ).exclude(id=id).exists()
        if overlap:
            return None
        try:
            vac = await Vacations.get_or_none(id=id)
        except DoesNotExist:
            return None
        await vac.update_from_dict(vacation.model_dump(exclude_none=True))
        await vac.save()
        return vac

    @classmethod
    async def delete_vacation(cls,id: int) -> bool:
        '''Функция для удаления отпуска или командировки'''
        vacation = await Vacations.get_or_none(id=id)
        if vacation:
            await vacation.delete()
            return vacation
        return vacation
