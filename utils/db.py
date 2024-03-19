from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INT, VARCHAR, Sequence, FLOAT
from configs.config import bind,bind_a
from sqlalchemy import text
from sqlalchemy import update

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'None Name'
    id = Column(INT, Sequence('bulletdata_id_seq'), primary_key=True)

class Database:
    def __init__(self, AsyncMode=True):
        """
        初始化数据库连接和Session
        """

        self.engine = create_engine(bind)
        self.Session = sessionmaker(self.engine, expire_on_commit=False)
        if AsyncMode == True:
            self.engine_async = create_async_engine(bind_a, echo=True)
            self.Session_async = sessionmaker(self.engine_async, expire_on_commit=False, class_=AsyncSession)

    def add_entity(self, entity_type, **kwargs):
        """
        同步添加实体
        :param entity_type: 实体类型
        :param kwargs: 实体属性
        """
        with self.Session() as session:
            entity = entity_type(**kwargs)
            session.add(entity)
            session.commit()

    async def add_entity_async(self, entity_type, **kwargs):
        """
        异步添加实体
        :param entity_type: 实体类型
        :param kwargs: 实体属性
        """
        async with self.Session_async() as session:
            entity = entity_type(**kwargs)
            session.add(entity)
            await session.commit()

    def get_entities(self, entity_type, filter_condition):
        """
        同步获取实体
        :param entity_type: 实体类型
        :param filter_condition: 过滤条件
        """
        with self.Session() as session:
            result = session.query(entity_type).filter(filter_condition).all()
            return result

    async def get_entities_async(self, entity_type, filter_condition):
        """
        异步获取实体
        :param entity_type: 实体类型
        :param filter_condition: 过滤条件
        """
        async with self.Session_async() as session:
            result = await session.run_sync(lambda session: session.query(entity_type).filter(filter_condition).all())
            return result
    
    def update_entity(self, entity_type, filter_condition, **kwargs):
        """
        同步更新实体
        :param entity_type: 实体类型
        :param filter_condition: 过滤条件
        :param kwargs: 更新的属性
        """
        with self.Session() as session:
            session.query(entity_type).filter(filter_condition).update(kwargs)
            session.commit()
    
    async def update_entity_async(self, entity_type, filter_condition, **kwargs):
        """
        异步更新实体
        :param entity_type: 实体类型
        :param filter_condition: 过滤条件
        :param kwargs: 更新的属性
        """
        async with self.Session_async() as session:
            update_stmt = update(entity_type).where(filter_condition).values(**kwargs)
            await session.execute(update_stmt)
            await session.commit()

    def delete_entity(self, entity_type, filter_condition):
        """
        同步删除实体
        :param entity_type: 实体类型
        :param filter_condition: 过滤条件
        """
        with self.Session() as session:
            session.query(entity_type).filter(filter_condition).delete()
            session.commit()

    async def delete_entity_async(self, entity_type, filter_condition):
        """
        异步删除实体
        :param entity_type: 实体类型
        :param filter_condition: 过滤条件
        """
        async with self.Session_async() as session:
            await session.run_sync(lambda: session.query(entity_type).filter(filter_condition).delete())
            await session.commit()

    def execute_sql_file(self, file_path):
        """
        执行SQL文件
        :param file_path: SQL文件路径
        """
        with open(file_path, 'r') as file:
            sql_commands = file.read()

        with self.Session() as session:
            session.execute(text(sql_commands))
            session.commit()

    def create_database_if_not_exists(self, db_name, sql_file_path):
        """
        如果数据库不存在，则创建数据库并执行SQL文件创建数据库结构
        :param db_name: 数据库名称
        :param sql_file_path: SQL文件路径
        """
        with self.engine.connect() as connection:
            result = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
            exists = result.first() is not None
            if not exists:
                connection.execute(text(f"CREATE DATABASE {db_name}"))
                new_engine = create_engine(bind.replace(bind.split('/')[-1], db_name))
                print(bind.replace(bind.split('/')[-1], db_name))
                with new_engine.connect() as new_connection:
                    with open(sql_file_path, 'r', encoding='utf-8') as file:
                        sql_commands = file.read()
                    new_connection.execute(text(sql_commands))
    


def create_database_and_structure_if_not_exists(db_name, sql_file_path):
    """
    检查数据库是否存在，如果不存在则创建数据库并从SQL文件中创建数据库结构
    :param db_name: 数据库名称
    :param sql_file_path: SQL文件路径
    """
    # 替换以下信息为你自己的数据库连接信息
    db_url = bind.replace(bind.split('/')[-1], '')
    engine = create_engine(db_url)

    with engine.connect() as connection:
        result = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
        exists = result.first() is not None
        if not exists:
            connection.execute(text(f"CREATE DATABASE {db_name}"))
            new_engine = create_engine(bind.rsplit('/', 1)[0] + '/' + db_name)
            with new_engine.connect() as new_connection:
                with open(sql_file_path, 'r', encoding='utf-8') as file:
                    sql_commands = file.read()
                new_connection.execute(text(sql_commands))



# # 替换以下信息为你自己的数据库连接信息
# db_url = 'mysql://root:20040824@localhost:3306/tkf_bullet_data'
# database = Database(db_url)
#
# # 使用例子：
# # 插入商人测试数据
# database.add_entity(Traders, name='peacekeeper', price=100, currency='USD')
# database.add_entity(Traders, name='skier', price=200, currency='EUR')
#
#
# # 获取商人
# trader = database.get_entity_by_attribute(Traders, 'name', 'peacekeeper')
#
# # 更新商人
# database.update_entity_attribute(Traders, trader.id, 'price', 200)
#
# # 删除商人
# database.delete_entity(Traders, trader.id)
#
# # 获取所有商人
# traders = database.get_all_entities(Traders)
# for trader in traders:
#     print(trader.name, trader.price, trader.currency)
