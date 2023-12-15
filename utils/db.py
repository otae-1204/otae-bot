from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector
from mysql.connector import Error
from configs.config import bind as db_connection_string, address, user, password, database
from configs.path_config import SQL_PATH

Base = declarative_base()


class Entity(Base):
    """
    定义一个通用的实体类
    
    使用例子：
    class User(Entity):
        __tablename__ = 'users'
        id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
        name = Column(String(50))
        fullname = Column(String(50))
        password = Column(String(12))
    """
    __abstract__ = True
    id = Column(Integer, Sequence('entity_id_seq'), primary_key=True)


class Database:
    sql_file_path = SQL_PATH + "db_otaebot.sql"

    def __init__(self, db_url):
        """
        初始化数据库连接和Session
        :param db_url: 数据库连接URL
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def add_entity(self, entity_type, **kwargs):
        """
        向数据库中添加任意类型的实体
        :param entity_type: 实体类型，例如User
        :param kwargs: 实体属性
        使用例子：
        db.add_entity(User, id=1, name='otaebot')
        """
        entity = entity_type(**kwargs)
        session = self.Session()
        session.add(entity)
        session.commit()
        session.close()
    
    async def add_entity_async(self, entity_type, **kwargs):
        """
        向数据库中添加任意类型的实体
        :param entity_type: 实体类型，例如User
        :param kwargs: 实体属性
        使用例子：
        await db.add_entity(User, id=1, name='otaebot')
        """
        entity = entity_type(**kwargs)
        session = self.Session()
        session.add(entity)
        await session.commit()
        session.close()
    
    def get_entity_by_attribute(self, entity_type, attribute, value):
        """
        根据属性查询任意类型的实体
        :param entity_type: 实体类型，例如User
        :param attribute: 属性名
        :param value: 属性值
        :return: 查询到的实体对象
        使用例子：
        db.get_entity_by_attribute(User, 'id', 1)
        """
        session = self.Session()
        query = session.query(entity_type).filter(getattr(entity_type, attribute) == value)
        entity = query.first()
        session.close()
        return entity
    
    async def get_entity_by_attribute_async(self, entity_type, attribute, value):
        """
        根据属性查询任意类型的实体
        :param entity_type: 实体类型，例如User
        :param attribute: 属性名
        :param value: 属性值
        :return: 查询到的实体对象
        使用例子：
        await db.get_entity_by_attribute(User, 'id', 1)
        """
        session = self.Session()
        query = session.query(entity_type).filter(getattr(entity_type, attribute) == value)
        entity = await query.first()
        session.close()
        return entity

    def update_entity_attribute(self, entity_type, identifier, attribute, new_value):
        """
        更新任意类型实体的属性
        :param entity_type: 实体类型，例如User
        :param identifier: 实体标识符，通常是id
        :param attribute: 属性名
        :param new_value: 新属性值
        使用例子：
        db.update_entity_attribute(User, 123456, 'name', 'otaebot')
        """
        session = self.Session()
        entity = session.query(entity_type).filter_by(id=identifier).first()
        if entity:
            setattr(entity, attribute, new_value)
            session.commit()
        session.close()
        
    async def update_entity_attribute_async(self, entity_type, identifier, attribute, new_value):
        """
        更新任意类型实体的属性
        :param entity_type: 实体类型，例如User
        :param identifier: 实体标识符，通常是id
        :param attribute: 属性名
        :param new_value: 新属性值
        使用例子：
        await db.update_entity_attribute(User, 123456, 'name', 'otaebot')
        """
        session = self.Session()
        entity = await session.query(entity_type).filter_by(id=identifier).first()
        if entity:
            setattr(entity, attribute, new_value)
            await session.commit()
        session.close()

    def delete_entity(self, entity_type, identifier):
        """
        删除任意类型的实体
        :param entity_type: 实体类型，例如User
        :param identifier: 实体标识符，通常是id
        使用例子：
        db.delete_entity(User, 123456)
        """
        session = self.Session()
        entity = session.query(entity_type).filter_by(id=identifier).first()
        if entity:
            session.delete(entity)
            session.commit()
        session.close()
        
    async def delete_entity_async(self, entity_type, identifier):
        """
        删除任意类型的实体
        :param entity_type: 实体类型，例如User
        :param identifier: 实体标识符，通常是id
        使用例子：
        await db.delete_entity_async(User, 123456)
        """
        session = self.Session()
        entity = await session.query(entity_type).filter_by(id=identifier).first()
        if entity:
            session.delete(entity)
            await session.commit()
        session.close()

    def get_all_entities(self, entity_type):
        """
        获取所有任意类型的实体
        :param entity_type: 实体类型，例如User
        :return: 实体列表
        使用例子：
        db.get_all_entities(User)
        """
        session = self.Session()
        entities = session.query(entity_type).all()
        session.close()
        return entities
    
    async def get_all_entities_async(self, entity_type):
        """
        获取所有任意类型的实体
        :param entity_type: 实体类型，例如User
        :return: 实体列表
        使用例子：
        await db.get_all_entities_async(User)
        """
        session = self.Session()
        entities = await session.query(entity_type).all()
        session.close()
        return entities

    def execute_sql_file(self, connection, sql_file_path):
        """
        执行 SQL 文件
        :param connection: 数据库连接
        :param sql_file_path: SQL 文件路径
        使用例子：
        db.execute_sql_file(connection, 'sql_file.sql')
        """
        try:
            cursor = connection.cursor()

            with open(sql_file_path, 'r') as sql_file:
                sql_statements = sql_file.read().split(';')

                for statement in sql_statements:
                    if statement.strip():
                        cursor.execute(statement)

            connection.commit()
            print(f"SQL file '{sql_file_path}' executed successfully.")

        except Error as e:
            print(f"Error: {e}")

        finally:
            if connection.is_connected():
                cursor.close()

    def check_db_connection(self):
        """
        检查数据库连接，如果数据库不存在则创建数据库并执行SQL文件
        """
        try:
            # 建立数据库连接
            connection = mysql.connector.connect(database=db_connection_string)
            print("数据库连接成功！")

        except Error as e:
            # 如果数据库不存在，则捕获错误并创建数据库
            if "Unknown database" in str(e):
                print(f"数据库不存在，正在创建数据库...")
                connection = mysql.connector.connect(host=address, user=user, password=password)
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE {database}")
                print("数据库创建成功！")
                connection.close()

                # 重新连接到新创建的数据库
                connection = mysql.connector.connect(database=db_connection_string)

                # 执行 SQL 文件
                self.execute_sql_file(connection, self.sql_file_path)
                print("数据库初始化成功！")

            else:
                print(f"Error: {e}")

        finally:
            # 关闭连接
            if connection.is_connected():
                connection.close()
                print("数据库连接已关闭！")









# # 替换以下信息为你自己的数据库连接信息
# db_url = 'mysql://root:20040824@localhost:3306/tkf_bullet_data'
# database = Database(db_url)

# # 使用例子：
# # 插入商人测试数据
# database.add_entity(Traders, name='peacekeeper', price=100, currency='USD')
# database.add_entity(Traders, name='skier', price=200, currency='EUR')


# # 获取商人
# trader = database.get_entity_by_attribute(Traders, 'name', 'peacekeeper')

# # 更新商人
# database.update_entity_attribute(Traders, trader.id, 'price', 200)

# # 删除商人
# database.delete_entity(Traders, trader.id)

# # 获取所有商人
# traders = database.get_all_entities(Traders)
# for trader in traders:
#     print(trader.name, trader.price, trader.currency)