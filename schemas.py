'''schemas.py'''

from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import EmailStr, field_validator

class YesNo(str, Enum):
    '''Класс схемы отпуска и командировки для уточнения'''
    YES = 'yes'
    NO = 'no'

class Employee(BaseModel):
    '''Класс схемы работника'''
    id: int
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None
    login:str | None = None
    password:str | None = None
    is_supervisor: YesNo  = Field(description="Type of string: 'yes' or 'no'")
    is_vacation: YesNo = Field(description="Type of string: 'yes' or 'no'")

    @field_validator('last_name', 'first_name', 'patronymic', 'email', 'login')
    def to_lower(cls, v):
        '''Функция для смены регистра в нижний предел'''
        return v.lower() if isinstance(v, str) else v

    class ConfigDict:
        '''Класс настройки'''
        from_attributes = True

class EmployeeAdd(BaseModel):
    '''Класс схемы работника для добавления'''
    last_name: str
    first_name: str
    patronymic: str | None = None
    email: EmailStr | None = None
    login:str | None = None
    password:str | None = None
    is_supervisor: YesNo  = Field(description="Type of string: 'yes' or 'no'")
    is_vacation: YesNo = Field(description="Type of string: 'yes' or 'no'")

    @field_validator('last_name', 'first_name', 'patronymic', 'email', 'login')
    def to_lower(cls, v):
        '''Функция для смены регистра в нижний предел'''
        return v.lower() if isinstance(v, str) else v

class EmployeeUpdate(BaseModel):
    '''Класс схемы работника для обновления'''
    id : int
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None
    login:str | None = None
    password:str | None = None
    is_supervisor: YesNo  = Field(description="Type of string: 'yes' or 'no'")
    is_vacation: YesNo = Field(description="Type of string: 'yes' or 'no'")

    @field_validator('last_name', 'first_name', 'patronymic', 'email', 'login')
    def to_lower(cls, v):
        '''Функция для смены регистра в нижний предел'''
        return v.lower() if isinstance(v, str) else v

class EmployeeSearch(BaseModel):
    '''Класс схемы работника для поиска'''
    id: int | None = None
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None
    login:str | None = None

    @field_validator('last_name', 'first_name', 'patronymic', 'email', 'login')
    def to_lower(cls, v):
        '''Функция для смены регистра в нижний предел'''
        return v.lower() if isinstance(v, str) else v

class EmployeeDelete(BaseModel):
    '''Класс схемы работника для удаления'''
    id:int

class VacationType(str, Enum):
    '''Класс схемы отпуска и командировки для уточнения'''
    VACATION = 'vacation'
    BUSINESS = 'business'

class Vacation(BaseModel):
    '''Класс схемы отпуска или командировки'''
    id: int
    employee_id : int | None = None
    type: VacationType = Field(description="Type of string: 'vacation' or 'business'")
    start_date: date | None = None
    end_date: date | None = None

class EmployeeWithVacations(BaseModel):
    '''Класс схемы отпуска или командировки с работником'''
    id: int
    last_name: Optional[str]
    first_name: Optional[str]
    patronymic: Optional[str]
    email: Optional[str]
    login: Optional[str]
    password: Optional[str]
    vacations: List[Vacation]

    class ConfigDict:
        '''Класс настройки для схемы отпуска или командировки с работником'''
        from_attributes = True

class VacationAdd(BaseModel):
    '''Класс схемы отпуска или командировки,для добавления'''
    employee_id: int
    type: VacationType = Field(description="Type of string: 'vacation' or 'business'")
    start_date: date | None = None
    end_date: date | None = None

class VacationUpdate(BaseModel):
    '''Класс схемы отпуска или командировки,дял обновления'''
    id: int
    employee_id: int | None = None
    type: VacationType = Field(description="Type of string: 'vacation' or 'business'")
    start_date: date | None = None
    end_date: date | None = None

class VacationDelete(BaseModel):
    '''Класс схемы отпуска или командировки для удаления'''
    id:int

class Subdivision(BaseModel):
    '''Класс схемы подразделения'''
    id: int
    name: str
    leader_id: int | None = None
    employee_ids: List[int]

    @field_validator('name')
    def to_lower(cls, v):
        '''Функция для смены регистра в нижний предел'''
        return v.lower() if isinstance(v, str) else v

    class ConfigDict:
        '''Класс настройки для схемы подразделений'''
        from_attributes = True

class SubdivisionAdd(BaseModel):
    '''Класс схемы подразделения для добавления'''
    id: int
    name: str
    leader_id: int | None = None

class SubdivisionLeaderUpdate(BaseModel):
    '''Класс схемы подразделения для добавления руководителя'''
    name : str
    leader_id: int | None = None

class SubdivisionEmployeeAdd(BaseModel):
    '''Класс схемы подразделения для добавления работника'''
    id: int
    name: str

class SubdivisionUpdate(BaseModel):
    '''Класс схемы подразделения для обновления'''
    id : int
    name: str

    @field_validator('name')
    def to_lower(cls, v):
        '''Функция для смены регистра в нижний предел'''
        return v.lower() if isinstance(v, str) else v

class SubdivisionDelete(BaseModel):
    '''Класс схемы подразделения для удаления'''
    id: int
