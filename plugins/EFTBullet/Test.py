from db import DatabaseDao

conditions = [["*5.56", "55A"], ["*5.45", "BT"]]


db = DatabaseDao()
list = db.selectAmmoByDiverse(conditions)
print(list)


