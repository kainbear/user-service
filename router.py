'''router.py'''

from typing import Annotated, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from psycopg2 import IntegrityError
from models import Employees
from schemas import Employee, EmployeeAdd, EmployeeUpdate, EmployeeWithVacations
from schemas import SubdivisionAdd, SubdivisionLeaderUpdate
from schemas import Vacation, VacationAdd, VacationUpdate, VacationType
from schemas import Subdivision, SubdivisionUpdate, SubdivisionEmployeeAdd
from repository import Repository

employee_router = APIRouter(prefix="/employee",
                            tags=["Employee Manager"])

SECRET_KEY = "kains"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    '''Функция для верификации пароля'''
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    '''Функция для получения хешированного пароля'''
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    '''Функция для создания доступа токена'''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@employee_router.get("/users/me")
async def get_current_user(login: str):
    '''Получение текущего пользователя по логину'''
    user = await Employees.get_or_none(login=login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@employee_router.post("/register")
async def register(user: Annotated[EmployeeAdd , Depends()]):
    '''Регистрация пользователя'''
    hashed_password = pwd_context.hash(user.password)
    user_data = user.model_dump()
    user_data['password'] = hashed_password

    try:
        new_employee = await Employees.create(**user_data)
        access_token = create_access_token(data={"sub": new_employee.login})
        return {"access_token": access_token, "token_type": "bearer"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email или логином уже существует")

@employee_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    '''Логин пользователя и получение токена'''
    user = await Employees.get_or_none(login=form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль")
    access_token = create_access_token(data={"sub": user.login})
    return {"access_token": access_token, "token_type": "bearer"}

@employee_router.get("/get_all", response_model=List[Employee])
async def read_all_employees():
    '''Функция для получения всех работников'''
    return await Repository.get_all_employees()

@employee_router.get("/{user_id}", response_model=Employee)
async def get_employee(user_id: int):
    '''Функция для получения работника по ID'''
    employee = await Repository.get_employee_by_id(user_id=user_id)
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    return employee

@employee_router.get("/search", response_model=List[Employee])
async def read_employee(
    last_name: Optional[str] = Query(default=None),
    first_name: Optional[str] = Query(default=None),
    patronymic: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    login: Optional[str] = Query(default=None),
):
    '''Функция для получения одного работника'''
    employee = await Repository.get_employee(
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        email=email,
        login=login,
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@employee_router.post("/add", response_model=Employee)
async def add_employee(employee: Annotated[EmployeeAdd, Depends()]):
    '''Функция для добавления работника'''
    employee = await Repository.add_employee(employee)
    # Если сотрудник уже есть, функция add_employee вернет None
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee aleardy exist")
    return employee

@employee_router.put("/update", response_model=EmployeeUpdate)
async def update_employee(id: int,employee: Annotated[EmployeeUpdate, Depends()]):
    '''Функция для обновления работника'''
    employee = await Repository.update_employee(id,employee)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@employee_router.delete("/{id}")
async def delete_employee(id:int):
    '''Функция для удаления работника'''
    success = await Repository.delete_employee(id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return { "detail":"Employee deleted"}

subdivision_router = APIRouter(prefix="/subdivision",
                               tags=["Subdivision Manager"])

@subdivision_router.get("/get_all", response_model=List[Subdivision])
async def read_all_subdivision():
    '''Функция для получения всех подразделений'''
    return await Repository.get_all_subdivisions()

@subdivision_router.get("/{subdivision_id}", response_model=Subdivision)
async def read_subdivision(subdivision_id: int):
    '''Функция для получения одного подразделения'''
    subdivision = await Repository.get_subdivision_by_id(subdivision_id)
    if subdivision is None:
        raise HTTPException(status_code=404, detail="Subdivision not found")
    return subdivision

@subdivision_router.post("/add", response_model=SubdivisionAdd)
async def add_subdivision(subdivision: Annotated[SubdivisionLeaderUpdate, Depends()]):
    '''Функция для добавления подразделения'''
    subdivision_data = subdivision.model_dump(exclude_unset=True)
    subdivision_name = subdivision_data.pop('name')
    leader_id = subdivision_data.pop('leader_id', None)
    new_subdivision = await Repository.add_subdivision(subdivision_name, leader_id)
    if not new_subdivision:
        raise HTTPException(status_code=404, detail="Subdivision already exist")
    return new_subdivision

@subdivision_router.put("/update/{subdivision_id}", response_model=SubdivisionUpdate)
async def update_subdivision(
    subdivision_id: int,
    name: str,
):
    '''Функция для обновления подразделения'''
    updated_subdivision = await Repository.update_subdivision(subdivision_id, name=name)
    if updated_subdivision is None:
        raise HTTPException(status_code=404, detail="Subdivision not found")
    return updated_subdivision

@subdivision_router.put("/{subdivision_id}/assign_leader/{leader_id}",
            response_model=SubdivisionLeaderUpdate)
async def assign_leader(
    subdivision_id: int,
    leader_id: int = Path(..., description="ID руководителя (является ID сотрудника)")
    ):
    '''Функция для добавления руководителя к подразделению'''
    updated_subdivision = await Repository.assign_leader(subdivision_id, leader_id)
    if not updated_subdivision:
        raise HTTPException(status_code=404, detail="Subdivision or Leader not found")
    return updated_subdivision

@subdivision_router.put("/assign_employee", response_model=SubdivisionEmployeeAdd)
async def assign_employee_to_subdivision(
    subdivision_id: int = Query(..., description="ID Subdivision"),
    employee_id: int = Query(..., description="ID Employee")
):
    '''Функция для прикрепления работника в подразделение'''
    subdivision = await Repository.assign_employee_to_subdivision(subdivision_id, employee_id)
    if subdivision is None:
        raise HTTPException(status_code=404, detail="Subdivision or Employee not found")
    return subdivision

@subdivision_router.delete("/{subdivision_id}/employee/{employee_id}", response_model=Subdivision)
async def remove_employee_from_subdivision(
    subdivision_id: int,
    employee_id: int
):
    '''Функция для открепления из подразделения'''
    subdivision = await Repository.remove_employee_from_subdivision(subdivision_id, employee_id)
    if subdivision is None:
        raise HTTPException(status_code=404, detail="Subdivision or Employee not found")
    return subdivision

@subdivision_router.delete("/{id}")
async def delete_subdivision(id: int):
    '''Функция для удаления подразделения'''
    success = await Repository.delete_subdivision(id)
    if not success:
        raise HTTPException(status_code=404, detail="Subdivision not found")
    return {"detail": "Subdivision deleted"}

vacation_router = APIRouter(prefix="/business_and_vacations",
                            tags=["Business and Vacations Manager"])

@vacation_router.get("/get_all", response_model=List[Vacation])
async def read_company_vacations_and_business():
    '''Функция для получения всех отпусков и командировок работников'''
    return await Repository.get_all_vacations()

@vacation_router.get("/search", response_model=List[EmployeeWithVacations])
async def get_employees_with_vacations(
    employee_id: Optional[int] = Query(default=None),
    type: VacationType = Query(..., description="Type of leave: 'vacation' or 'business'")
):
    '''Функция для получения работника с отпусками или командировками'''
    employees = await Repository.get_employee_with_vacations(employee_id=employee_id, type=type)
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found")
    return employees

@vacation_router.post("/add", response_model=Vacation)
async def add_vacations_or_business(
    vacation: Annotated[VacationAdd,Depends()],
    type: str = Query(default=None, description="Type of leave: 'vacation' or 'business'")
                                    ):
    '''Функция для добавления отпуски или командировки'''
    vacation = await Repository.add_vacation(vacation)
    if vacation is None:
        raise HTTPException(status_code=404, detail="Date already in use,use another")
    return vacation

@vacation_router.put("/update", response_model=VacationUpdate)
async def update_vacations_or_business(id: int,vacation: Annotated[VacationUpdate, Depends()]):
    '''Функция для обновления отпуска или командировки'''
    vacation = await Repository.update_vacation(id,vacation)
    if vacation is None:
        raise HTTPException(status_code=404, detail="Date already in use,use another")
    return vacation

@vacation_router.delete("/{id}")
async def delete_vacations_or_business(id: int):
    '''Функция для удаления отпуска или командировки'''
    success = await Repository.delete_vacation(id)
    if not success:
        raise HTTPException(status_code=404, detail="Business And Vacation not found")
    return { "detail":"Busines And Vacation delete"}
