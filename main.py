''' main.py'''

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import aerich_config
from router import employee_router
from router import subdivision_router
from router import vacation_router

app = FastAPI(
        title="User-Service",
        version="1.0.0",
        description="Сервис для создания и хранения данных о работниках.",
    )

app.include_router(employee_router)
app.include_router(subdivision_router)
app.include_router(vacation_router)


register_tortoise(
    app,
    db_url=aerich_config.DATABASE_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
    )
