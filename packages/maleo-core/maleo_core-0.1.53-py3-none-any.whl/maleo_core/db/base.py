from sqlalchemy.orm import as_declarative, declared_attr

@as_declarative()
class Base:
    id:int
    __name__:str

    #* Automatically generate table names if not provided
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()