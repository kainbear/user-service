'''aerich_config.py'''

DATABASE_URL = "postgres://kainbear:sups4@postgres-users:5432/users"

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models" : {
            "models" : ["models","aerich.models"],
            "default_connection": "default",
        },
    },
}
