import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.orm as Session

SqlAlchemyBase = orm.declarative_base()

factory = None

def global_init(db_file):
    global factory
    if factory: return

    if not db_file or not db_file.strip():
        raise Exception('Необходимо указать файл базы данных')
    
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f'Подключение к базе данных по адресу {conn_str}')

    engine = sa.create_engine(conn_str, echo=False)
    factory = orm.sessionmaker(bind=engine)
    print(factory)
    SqlAlchemyBase.metadata.create_all(engine)

def create_session() -> Session:
    global factory
    return factory()