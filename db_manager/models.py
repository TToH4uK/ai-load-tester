from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FAQ(Base):
    __tablename__ = "faq"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, unique=True, index=True)
    answer = Column(Text)