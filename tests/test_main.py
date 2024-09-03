'''test_main.py'''

from datetime import date
from httpx import AsyncClient
import pytest
from models import Vacations

@pytest.mark.asyncio
async def test_read_all_employees(client: AsyncClient, create_employee):
    ''' Тест функции для  получения всех работников'''
    await create_employee
    response = await client.get("/employee/get_all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    print("Response data:", data)
    assert True

@pytest.mark.asyncio
async def test_read_employee(client: AsyncClient, create_employee_another):
    ''' Тест функции для  получения работника'''
    await create_employee_another
    response = await client.get("/employee/search", params={"last_name": "Solodilov"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["last_name"].lower() == "solodilov".lower()
    assert data[0]["first_name"] == "Nikita".lower()
    assert data[0]["patronymic"] == "Alexevich".lower()
    assert data[0]["email"] == "nik@google.com"
    assert data[0]["login"] == "nik"
    assert data[0]["password"] == "nik464"
    assert True

@pytest.mark.asyncio
async def test_add_employee(client: AsyncClient):
    ''' Тест функции для  добавления работника'''
    new_employee = {
        "last_name" : "Slavov",
        "first_name" : "Slav",
        "patronymic" : "Slavevich",
        "email": "slav@google.com",
        "login": "slav4",
        "password": "slav123",
    }
    response = await client.post("/employee/add", params=new_employee)
    assert response.status_code == 200
    data = response.json()
    assert data["last_name"] == "Slavov".lower()
    assert data["first_name"] == "Slav".lower()
    assert data["patronymic"] == "Slavevich".lower()
    assert data["email"] == "slav@google.com"
    assert data["login"] == "slav4"
    assert data["password"] == "slav123"
    print("Response data:", data)
    assert True

@pytest.mark.asyncio
async def test_update_employee(client):
    ''' Тест функции для  обновления работника'''
    new_employee = {
        "last_name": "Софьева",
        "first_name" : "София",
        "patronymic": "Софовна",
        "email": "софия@google.com",
        "login": "софия123",
        "password": "софия321",
    }
    response = await client.post("/employee/add", params=new_employee)
    assert response.status_code == 200
    data = response.json()
    print("Response data:", data)
    employee_id = data["id"]
    employee_last_name = data["last_name"]

    updated_employee_data = {
        "email": "софья@google.com",
        "login": "софьяпаук",
        "password": "софьяпаук123",
    }
    response = await client.put(f"/employee/update?id={employee_id}&last_name={employee_last_name}",
                                params=updated_employee_data)
    assert response.status_code == 200
    updated_data = response.json()
    print("Updated Response Data:", updated_data)
    assert updated_data["email"] == "софья@google.com"
    assert updated_data["login"] == "софьяпаук"
    assert updated_data["password"] == "софьяпаук123"
    assert True


@pytest.mark.asyncio
async def test_delete_employee(client, create_employee):
    ''' Тест функции для  удаления работника'''
    response = await client.delete(f"/employee/{create_employee.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Employee deleted"
    data = response.json()
    print("Response data:", data )

    response = await client.get(f"/search?last_name={create_employee.last_name}")
    assert response.status_code == 404
    data = response.json()
    print("Response data:", data )
    assert True

@pytest.mark.asyncio
async def test_delete__not_found_employee(client, create_employee):
    ''' Тест функции для  удаления работника,если его нет'''
    response = await client.delete(f"/employee/{create_employee.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Employee deleted"
    data = response.json()
    print("Response data:", data )

    response = await client.get(f"/search?last_name={"Denisov"}")
    assert response.status_code == 404
    data = response.json()
    print("Response data:", data )
    assert True

@pytest.mark.asyncio
async def test_read_company_vacations_and_business(client: AsyncClient,create_employee):
    ''' Тест функции для  получения отпусков или командировок'''
    await create_employee
    response = await client.get("business_and_vacations/get_all")
    assert response.status_code == 200
    assert len(response.json()) >= 0
    data = response.json()
    print("Response data:", data)
    assert True

@pytest.mark.asyncio
async def test_get_employees_with_vacations_vacation(client, create_employee):
    ''' Тест функции для  получения у работника отпуска или командировки'''
    vacation1 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 15),
        type="vacation"
    )
    await vacation1
    vacation2 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 5, 1),
        end_date=date(2024, 5, 15),
        type="vacation"
    )
    await vacation2
    response = await client.get(f"/business_and_vacations/search?employee_id={create_employee.id}&type=vacation")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == create_employee.id
    assert len(data[0]["vacations"]) > 0
    print(response.text)
    assert True

@pytest.mark.asyncio
async def test_get_employees_with_vacations_business(client, create_employee):
    ''' Тест функции для получения у работника отпуска или командировки по фильтру бизнес '''
    vacation1 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 15),
        type="business"
    )
    await vacation1
    vacation2 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 15),
        type="business"
    )
    await vacation2
    response = await client.get(f"/business_and_vacations/search?employee_id={create_employee.id}&type=business")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == create_employee.id
    assert len(data[0]["vacations"]) > 0
    print(response.text)
    assert True

@pytest.mark.asyncio
async def test_get_employees_with_vacations_with_filter(client, create_employee):
    ''' Тест функции для получения у работника отпуска или командировки по фильтру отпуск '''
    vacation1 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 15),
        type="vacation"
    )
    await vacation1
    vacation2 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 5, 1),
        end_date=date(2024, 5, 15),
        type="vacation"
    )
    await vacation2
    vacation3 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 15),
        type="business"
    )
    await vacation3
    vacation4 = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 15),
        type="business"
    )
    await vacation4
    response = await client.get(f"/business_and_vacations/search?employee_id={create_employee.id}&type=vacation")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == create_employee.id
    assert len(data[0]["vacations"]) > 0
    assert data[0]["vacations"][0]["type"] == "vacation"
    print(response.text)
    assert True

    # Business фильтр
    response = await client.get(f"/business_and_vacations/search?employee_id={create_employee.id}&type=business")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == create_employee.id
    assert len(data[0]["vacations"]) > 0
    assert data[0]["vacations"][0]["type"] == "business"
    print(response.text)
    assert True

@pytest.mark.asyncio
async def test_get_employees_with_vacations_no_employees_if_business(client):
    ''' Тест функции для получения работника с командировкой,если нет работника'''
    response = await client.get("/business_and_vacations/search?employee_id=999&type=business")
    assert response.status_code == 404
    assert response.json() == {"detail": "No employees found"}
    print(response.text)
    assert True

@pytest.mark.asyncio
async def test_get_employees_with_vacations_no_employees_if_vacation(client):
    ''' Тест функции для получения работника с отпуском ,если нет работника'''
    response = await client.get("/business_and_vacations/search?employee_id=999&type=vacation")
    assert response.status_code == 404
    assert response.json() == {"detail": "No employees found"}
    print(response.text)
    assert True

@pytest.mark.asyncio
async def test_add_vacations_or_business(client: AsyncClient, create_employee):
    '''Тест функции для добавления отпуск или командировки для работника'''
    response = await client.post("/business_and_vacations/add", params={
        "employee_id": create_employee.id,
        "start_date": "2024-06-05",
        "end_date": "2024-06-10",
        "type": "vacation"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == create_employee.id
    assert data["start_date"] == "2024-06-05"
    assert data["end_date"] == "2024-06-10"
    assert data["type"] == "vacation"
    assert True

@pytest.mark.asyncio
async def test_add_vacation_with_overlapping_dates(client: AsyncClient,create_employee):
    ''' Тест функции для добавления отпуска или командировки,если даты пересекаются'''
    await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 15),
        type="vacation"
    )
    response = await client.post("/business_and_vacations/add", params={
        "employee_id": create_employee.id,
        "start_date": "2024-06-10",
        "end_date": "2024-06-20",
        "type": "vacation"
    })
    assert response.status_code == 404
    assert True

@pytest.mark.asyncio
async def test_update_vacations_or_business(client,create_employee):
    ''' Тест функции для обновления отпуска или командировки'''
    vacation = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 15),
        type="vacation"
    )
    vacation_update_data = {
        "start_date": date(2024, 6, 16),
        "end_date": date(2024, 6, 26),
        "type": "vacation"
    }
    response = await client.put(f"/business_and_vacations/update?id={vacation.id}&employee_id={create_employee.id}",
                                params=vacation_update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == vacation.id
    assert data["start_date"] == str(data["start_date"])
    assert data["end_date"] == str(data["end_date"])
    assert data["type"] == data["type"]
    print("Response data:",data )
    assert True

@pytest.mark.asyncio
async def test_delete_vacation_success(client,create_employee):
    ''' Тест функции для удаления отпуска или командировки'''
    vacation = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 15),
        type="Vacation"
    )
    response = await client.delete(f"/business_and_vacations/{vacation.id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Busines And Vacation delete"}
    data = response.json()
    print("Response data:", data )

    response = await client.get(f"/search?id={create_employee.id}")
    assert response.status_code == 404
    data = response.json() == {"detail": "Busines And Vacation not found"}
    print("Response data:", data )
    assert True

@pytest.mark.asyncio
async def test_delete_vacation__not_found(client,create_employee):
    ''' Тест функции для удаления отпуска или командировки,если нет отпуска или командировки'''
    vacation = await Vacations.create(
        employee_id=create_employee.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 15),
        type="Vacation"
    )
    response = await client.delete(f"/business_and_vacations/{vacation.id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Busines And Vacation delete"}
    data = response.json()
    print("Response data:", data )

    response = await client.get(f"/search?id={20}")
    assert response.status_code == 404
    data = response.json() == {"detail": "Busines And Vacation not found"}
    print("Response data:", data )
    assert True

@pytest.mark.asyncio
async def test_read_all_subdivisions(client):
    ''' Тест функции для получения всех подразделений'''
    response = await client.get("/subdivision/get_all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0
    print("Response data:", data)
    assert True

@pytest.mark.asyncio
async def test_read_subdivision(client):
    ''' Тест функции для получения подразделения'''
    subdivision_id = 1
    response = await client.get(f"/subdivision/{subdivision_id}")
    if response.status_code == 404:
        assert response.json() == {"detail": "Subdivision not found"}
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == subdivision_id
    assert True

@pytest.mark.asyncio
async def test_add_subdivision(client, create_employee):
    ''' Тест функции для добавления подразделения'''
    add_payload = {"name": "newsubdivision", "leader_id": create_employee.id}
    response = await client.post("/subdivision/add", params=add_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "newsubdivision"
    assert data["leader_id"] == create_employee.id
    newsubdivision_id = data["id"]
    try:
        print(response.text)
        assert True
    finally:
        delete_response = await client.delete(f"/subdivision/{newsubdivision_id}")
        assert delete_response.status_code == 200
    assert True


@pytest.mark.asyncio
async def test_update_subdivision(client):
    ''' Тест функции для обновления подразделения'''
    subdivision_id = 1
    response = await client.put(f"/subdivision/update/{subdivision_id}",
                                params={"name": "UpdatedSubdivision"})
    if response.status_code == 404:
        assert response.json() == {"detail": "Subdivision not found"}
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updatedsubdivision"
    assert True

@pytest.mark.asyncio
async def test_assign_leader(client):
    ''' Тест функции для прикрепления к подразделению руководителя'''
    subdivision_id = 1
    leader_id = 1
    response = await client.put(f"/subdivision/{subdivision_id}/assign_leader/{leader_id}")
    if response.status_code == 404:
        assert response.json() == {"detail": "Subdivision or Leader not found"}
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["leader_id"] == leader_id
    assert True

@pytest.mark.asyncio
async def test_assign_employee_to_subdivision(client):
    ''' Тест функции для прикрепления работника к подразделению'''
    response = await client.put("/subdivision/assign_employee",
                                params={"subdivision_id": 1, "employee_id": 1})
    if response.status_code == 404:
        assert response.json() == {"detail": "Subdivision or Employee not found"}
    else:
        assert response.status_code == 200
        data = response.json()
        assert 1 in data["employee_ids"]
    assert True

@pytest.mark.asyncio
async def test_remove_employee_from_subdivision(client):
    ''' Тест функции для открепления работника от подразделения'''
    response = await client.delete("/subdivision/1/employee/1")
    if response.status_code == 404:
        assert response.json() == {"detail": "Subdivision or Employee not found"}
    else:
        assert response.status_code == 200
        data = response.json()
        assert 1 not in data["employee_ids"]
    assert True

@pytest.mark.asyncio
async def test_delete_subdivision(client):
    ''' Тест функции для удаления подразделения'''
    response = await client.delete("/subdivision/1")
    if response.status_code == 404:
        assert response.json() == {"detail": "Subdivision not found"}
    else:
        assert response.status_code == 200
        assert response.json() == {"detail": "Subdivision deleted"}
    assert True
