from sqlalchemy import Column, Date, Integer, String , Float , Boolean
from agro_back.agro_backend.models.base import TimeStampedModel , Base 
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid


class Agro_Acc(TimeStampedModel):
    __tablename__ = "agro_users"
    farmer_id = Column(String , primary_key=True , index=True)
    farm_name = Column(String , index=True)
    farm_email = Column(String , unique=True, index=True, nullable=False)
    farm_livestocks = Column(Integer , index=True)
    hashed_password = Column(String, index=True)
    