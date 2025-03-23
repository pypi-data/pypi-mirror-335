import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# 📌 1. Базовый класс для таблиц
class Base(DeclarativeBase):
    pass


# 📌 2. Класс для работы с базой данных
class Db:
    def __init__(self, db_path="database.db", table_name="data", **columns):
        """Создаёт подключение и таблицу"""
        self.engine = create_engine(db_path)  # Локальная база
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # 🟢 Динамически создаём таблицу
        attrs = {"__tablename__": table_name.lower(), "id": Column(Integer, primary_key=True)}

        for col_name, col_data in columns.items():
            if isinstance(col_data, tuple):
                column_type = col_data[0]
                options = {opt.split("=")[0]: opt.split("=")[1] == "True" for opt in col_data[1:]}
            else:
                column_type = col_data
                options = {}

            if column_type == int:
                column_type = Integer
            elif column_type == str:
                column_type = String
            else:
                raise ValueError(f"Неизвестный тип данных: {column_type}")

            attrs[col_name] = Column(column_type, **options)

        self.TableClass = type(table_name, (Base,), attrs)  # Создаём модель
        Base.metadata.create_all(self.engine)  # Создаём таблицу

    def add(self, **kwargs):
        """Добавляет запись в таблицу"""
        try:
            new_entry = self.TableClass(**kwargs)
            self.session.add(new_entry)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка добавления: {e}")

    def delete(self, obj_id):
        """Удаляет запись по ID"""
        obj = self.session.get(self.TableClass, obj_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        else:
            print("Запись не найдена!")

    def update(self, obj_id, **kwargs):
        """Обновляет запись"""
        obj = self.session.get(self.TableClass, obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.session.commit()
        else:
            print("Запись не найдена!")

    def get_all(self, order_by=None, desc=False):
        """Получает все записи с сортировкой"""
        query = self.session.query(self.TableClass)
        if order_by:
            column = getattr(self.TableClass, order_by, None)
            if column:
                query = query.order_by(column.desc() if desc else column)
        return query.all()

    def get(self, obj_id):
        """Получает запись по ID"""
        return self.session.get(self.TableClass, obj_id)

    def get_by_one(self, **kwargs):
        """Возвращает **одного** пользователя по условию (или None, если нет)"""
        query = self.session.query(self.TableClass)
        for key, value in kwargs.items():
            column = getattr(self.TableClass, key, None)
            if column is not None:
                query = query.filter(column == value)
        return query.first()  # Возвращает одного или None

    def get_by_all(self, **kwargs):
        """Возвращает **всех** пользователей по условию"""
        query = self.session.query(self.TableClass)
        for key, value in kwargs.items():
            column = getattr(self.TableClass, key, None)
            if column is not None:
                query = query.filter(column == value)
        return query.all()  # Возвращает список объектов
