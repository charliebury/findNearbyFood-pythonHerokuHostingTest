from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


class User(Base):
    # a database of saved users
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    # hash a supplied password
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    # check if supplied password matches hashed one
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # create a token to avoid using password (will expire after some time)
    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # valid token, but expired
            return None
        except BadSignature:
            # invalid token
            return None
        user_id = data['id']
        return user_id


class previousSearches(Base):
    # a database of previous searches (by anyone)
    __tablename__ = 'bagel'
    id = Column(Integer, primary_key=True)
    location = Column(String)
    foodType = Column(String)

    @property
    def serialize(self):
        return {'location': self.location, 'foodType': self.foodType}

engine = create_engine('sqlite:///findFoodUsers.db')
Base.metadata.create_all(engine)
