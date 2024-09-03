'''models.py'''

from tortoise import fields
from tortoise.models import Model

class Employees(Model):
    '''Класс модели работников'''
    id = fields.IntField(pk=True)
    last_name = fields.CharField(64,null=True)
    first_name = fields.CharField(64,null=True)
    patronymic = fields.CharField(64,null=True)
    email = fields.CharField(64,null=True,UNIQUE=True)
    login = fields.CharField(50,null=True,unique=True)
    password = fields.CharField(128)
    is_supervisor = fields.CharField(max_length=5)  # 'yes' или 'no'
    is_vacation = fields.CharField(max_length=5) # 'yes' или 'no'

    class Meta:
        '''Класс имени таблицы работников'''
        table = "employees"

class Vacations(Model):
    '''Класс модели отпусков и командировок'''
    id = fields.IntField(pk=True)
    employee = fields.ForeignKeyField('models.Employees', related_name='vacations')
    start_date = fields.DateField(null=True)
    end_date = fields.DateField(null=True)
    type = fields.CharField(max_length=20)  # 'vacation' или 'business'

    class Meta:
        '''Класс имени модели отпусков и командировок'''
        table = "vacations"

class Subdivisions(Model):
    '''Класс модели подразделений'''
    id = fields.IntField(pk=True)
    name = fields.CharField(64, null=True,unique=True)
    employees = fields.ManyToManyField('models.Employees', related_name='subdivisions')
    leader = fields.ForeignKeyField('models.Employees', related_name='leaders', null=True)

    class Meta:
        '''Класс имени модели подразделений'''
        table = "subdivisions"
