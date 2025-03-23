from sqlalchemy3.orm import sessionmaker


class CRUD:
    def __init__(self, model, engine):
        """
        初始化CRUD类实例，并创建会话工厂。

        :param model: SQLAlchemy模型类，用于指定操作的数据库表。
        :param engine: SQLAlchemy引擎对象，用于连接数据库。
        """
        self.model = model
        self.Session = sessionmaker(bind=engine)

    def add(self, session=None, **kwargs):
        """
        添加一个新的记录到数据库。

        :param kwargs: 字典形式的参数，用于创建模型实例。
        :return: 创建的模型实例。
        """
        close_session = False
        if session is None:
            session = self.Session()
            close_session = True
        try:
            instance = self.model(**kwargs)
            session.add(instance)
            if close_session:
                session.commit()
                session.refresh(instance)
            return instance
        finally:
            if close_session:
                session.close()

    def update(self, id, session=None, **kwargs):
        """
        更新指定ID的记录。

        :param id: 记录的主键ID。
        :param kwargs: 字典形式的参数，用于更新模型实例。
        :return: 更新后的模型实例或None。
        """
        close_session = False
        if session is None:
            session = self.Session()
            close_session = True
        try:
            instance = session.query(self.model).get(id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                if close_session:
                    session.commit()
                    session.refresh(instance)
                return instance
            return None
        finally:
            if close_session:
                session.close()

    def delete(self, id, session=None):
        """
        删除指定ID的记录。

        :param id: 记录的主键ID。
        :return: 如果删除成功返回True，否则返回False。
        """
        close_session = False
        if session is None:
            session = self.Session()
            close_session = True
        try:
            instance = session.query(self.model).get(id)
            if instance:
                session.delete(instance)
                if close_session:
                    session.commit()
                return True
            return False
        finally:
            if close_session:
                session.close()

    # 查询方法保持不变
    def get(self, *args, **kwargs):
        session = self.Session()
        try:
            if args:
                return session.query(self.model).get(args[0])
            elif kwargs:
                return session.query(self.model).filter_by(**kwargs).first()
            return None
        finally:
            session.close()

    def get_all(self, **kwargs):
        """
        获取所有记录，支持过滤条件。

        :param kwargs: 过滤条件，例如 get_all(product_id=1)
        :return: 符合条件的所有记录列表。
        """
        session = self.Session()
        try:
            query = session.query(self.model)
            if kwargs:
                query = query.filter_by(**kwargs)
            return query.all()
        finally:
            session.close()

    def get_page(self, page=1, size=10):
        """
        分页查询记录。

        :param page: 页码，从1开始。
        :param size: 每页记录数。
        :return: 当前页的记录列表。
        """
        session = self.Session()
        try:
            query = session.query(self.model).offset((page - 1) * size).limit(size)
            return query.all()
        finally:
            session.close()

    def delete_all(self):
        """
        删除当前模型的所有记录
        返回删除的行数
        """
        session = self.Session()
        try:
            result = session.query(self.model).delete()
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
