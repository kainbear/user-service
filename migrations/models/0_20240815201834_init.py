from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "employees" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_name" VARCHAR(64),
    "first_name" VARCHAR(64),
    "patronymic" VARCHAR(64),
    "email" VARCHAR(64),
    "login" VARCHAR(50)  UNIQUE,
    "password" VARCHAR(128) NOT NULL,
    "is_supervisor" VARCHAR(5) NOT NULL,
    "is_vacation" VARCHAR(5) NOT NULL
);
COMMENT ON TABLE "employees" IS 'Класс модели работников';
CREATE TABLE IF NOT EXISTS "subdivisions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(64)  UNIQUE,
    "leader_id" INT REFERENCES "employees" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "subdivisions" IS 'Класс модели подразделений';
CREATE TABLE IF NOT EXISTS "vacations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "start_date" DATE,
    "end_date" DATE,
    "type" VARCHAR(20) NOT NULL,
    "employee_id" INT NOT NULL REFERENCES "employees" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "vacations" IS 'Класс модели отпусков и командировок';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "subdivisions_employees" (
    "subdivisions_id" INT NOT NULL REFERENCES "subdivisions" ("id") ON DELETE CASCADE,
    "employees_id" INT NOT NULL REFERENCES "employees" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
