from peewee import SqliteDatabase, Model

# 定义数据库对象
db = SqliteDatabase("magic_dash_pro.db")


class BaseModel(Model):
    """数据库表模型基类"""

    class Meta:
        # 关联数据库
        database = db
