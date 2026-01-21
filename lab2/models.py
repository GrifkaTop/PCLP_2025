from sqlalchemy import BigInteger, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class UserType(Base):
    __tablename__ = 'user_types'
    type_id: Mapped[int] = mapped_column(primary_key=True)
    permission: Mapped[bool] = mapped_column(Boolean, default=False)

class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('user_types.type_id'))

class Group(Base):
    __tablename__ = 'groups'
    group_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

class ULink(Base):
    __tablename__ = 'ulinks'
    ulink_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id'))

class Subject(Base):
    __tablename__ = 'subjects'
    subject_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

class Course(Base):
    __tablename__ = 'courses'
    course_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.subject_id'))

class Mark(Base):
    __tablename__ = 'marks'
    mark_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    task_id: Mapped[int] = mapped_column(Integer)
    value: Mapped[int] = mapped_column(Integer)

async def async_db_setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
