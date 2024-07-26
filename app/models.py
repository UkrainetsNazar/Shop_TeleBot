from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from aiogram.fsm.state import StatesGroup, State
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class AddCloth_Man(StatesGroup):
    бренд = State()
    розмір = State()
    вартість = State()
    стан = State()
    фото1 = State()
    фото2 = State()
    фото3 = State()
    фото4 = State()
    фото5 = State()
    tg_link = State()


class AddCloth_Woman(StatesGroup):
    бренд = State()
    розмір = State()
    вартість = State()
    стан = State()
    фото1 = State()
    фото2 = State()
    фото3 = State()
    фото4 = State()
    фото5 = State()
    tg_link = State()

class AddShoes_Man(StatesGroup):
    бренд = State()
    розмір = State()
    вартість = State()
    стан = State()
    фото1 = State()
    фото2 = State()
    фото3 = State()
    фото4 = State()
    фото5 = State()
    tg_link = State()


class AddShoes_Woman(StatesGroup):
    бренд = State()
    розмір = State()
    вартість = State()
    стан = State()
    фото1 = State()
    фото2 = State()
    фото3 = State()
    фото4 = State()
    фото5 = State()
    tg_link = State()


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ManCloth(Base):
    __tablename__ = 'чоловічий_одяг'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    бренд: Mapped[str] = mapped_column(String, nullable=False)
    розмір: Mapped[str] = mapped_column(String, nullable=False)
    вартість: Mapped[int] = mapped_column(Integer, nullable=False)
    стан: Mapped[int] = mapped_column(Integer, nullable=False)
    фото1: Mapped[str] = mapped_column(String, nullable=True)
    фото2: Mapped[str] = mapped_column(String, nullable=True)
    фото3: Mapped[str] = mapped_column(String, nullable=True)
    фото4: Mapped[str] = mapped_column(String, nullable=True)
    фото5: Mapped[str] = mapped_column(String, nullable=True)
    tg_link: Mapped[str] = mapped_column(String, nullable=False)  # For button Замовити


class WomanCloth(Base):
    __tablename__ = 'жіночий_одяг'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    бренд: Mapped[str] = mapped_column(String, nullable=False)
    розмір: Mapped[str] = mapped_column(String, nullable=False)
    вартість: Mapped[int] = mapped_column(Integer, nullable=False)
    стан: Mapped[int] = mapped_column(Integer, nullable=False)
    фото1: Mapped[str] = mapped_column(String, nullable=True)
    фото2: Mapped[str] = mapped_column(String, nullable=True)
    фото3: Mapped[str] = mapped_column(String, nullable=True)
    фото4: Mapped[str] = mapped_column(String, nullable=True)
    фото5: Mapped[str] = mapped_column(String, nullable=True)
    tg_link: Mapped[str] = mapped_column(String, nullable=False)


class ManShoes(Base):
    __tablename__ = 'чоловіче_взуття'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    бренд: Mapped[str] = mapped_column(String, nullable=False)
    розмір: Mapped[str] = mapped_column(String, nullable=False)
    вартість: Mapped[int] = mapped_column(Integer, nullable=False)
    стан: Mapped[int] = mapped_column(Integer, nullable=False)
    фото1: Mapped[str] = mapped_column(String, nullable=True)
    фото2: Mapped[str] = mapped_column(String, nullable=True)
    фото3: Mapped[str] = mapped_column(String, nullable=True)
    фото4: Mapped[str] = mapped_column(String, nullable=True)
    фото5: Mapped[str] = mapped_column(String, nullable=True)
    tg_link: Mapped[str] = mapped_column(String, nullable=False)  # For button Замовити


class WomanShoes(Base):
    __tablename__ = 'жіноче_взуття'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    бренд: Mapped[str] = mapped_column(String, nullable=False)
    розмір: Mapped[str] = mapped_column(String, nullable=False)
    вартість: Mapped[int] = mapped_column(Integer, nullable=False)
    стан: Mapped[int] = mapped_column(Integer, nullable=False)
    фото1: Mapped[str] = mapped_column(String, nullable=True)
    фото2: Mapped[str] = mapped_column(String, nullable=True)
    фото3: Mapped[str] = mapped_column(String, nullable=True)
    фото4: Mapped[str] = mapped_column(String, nullable=True)
    фото5: Mapped[str] = mapped_column(String, nullable=True)
    tg_link: Mapped[str] = mapped_column(String, nullable=False)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)