from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
# Импортируем Base из файла session
from db_manager.session import Base 

class FAQ(Base):
    __tablename__ = "faq"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    question_vector = Column(Vector(384))