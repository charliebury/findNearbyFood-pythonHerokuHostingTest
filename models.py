from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class previousSearches(Base):
    __tablename__ = 'bagel'
    id = Column(Integer, primary_key=True)
    location = Column(String)
    foodType = Column(String)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'location': self.location, 'foodType': self.foodType}

engine = create_engine('sqlite:///findFoodUsers.db')
Base.metadata.create_all(engine)
