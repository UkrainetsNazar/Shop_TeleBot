from sqlalchemy import BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ManCloth(Base):
    __tablename__ = 'чоловічий_одяг'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
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

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
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