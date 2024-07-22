from peewee import Model, SqliteDatabase, IntegerField, CharField

db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)

db.connect()
db.create_tables([User])