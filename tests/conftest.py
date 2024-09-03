'''conftest.py'''

from typing import AsyncGenerator
from contextlib import asynccontextmanager
import httpx
import pytest_asyncio
from fastapi import FastAPI
from tortoise import Tortoise
from models import Employees
from router import employee_router
from router import subdivision_router
from router import vacation_router

@pytest_asyncio.fixture
async def init_db()-> AsyncGenerator[None, None]:
    '''Функция для  инициализации бд для тестов'''
    await Tortoise.init(
         db_url="postgres://kainbear:sups4@127.0.0.1:5432/users",
         modules={'models': ['models']},)
    await Tortoise.generate_schemas()
    print("Tortoise is on")
    yield
    await Tortoise.close_connections()
    print("Tortoise is off")

@pytest_asyncio.fixture
async def app(init_db) -> AsyncGenerator[FastAPI, None]:
    '''Функция для жизненного цикла приложения для тестов'''
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(employee_router)
    app.include_router(subdivision_router)
    app.include_router(vacation_router)
    yield app

@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    '''Функция для имитации пользователя'''
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://127.0.0.1:8000"
        ) as client:
        print("Client is on")
        yield client
        print("Client is off")

@pytest_asyncio.fixture
async def create_employee():
    '''Функция для создания работника в тестовой бд'''
    employee = await Employees.create(
        last_name= "Denisov",
        first_name= "Stas",
        patronymic = "Alexevich",
        email= "stas@google.com",
        login= "stas",
        password= "stas464",
    )
    yield employee
    await employee.delete()

@pytest_asyncio.fixture
async def create_employee_another():
    '''Функция для создания другого работника в тестовой бд'''
    employee = await Employees.create(
        last_name = "Solodilov",
        first_name = "Nikita",
        patronymic = "Alexevich",
        email = "nik@google.com",
        login = "nik",
        password = "nik464",
    )
    yield employee
    await employee.delete()
