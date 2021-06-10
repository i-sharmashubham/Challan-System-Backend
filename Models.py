from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Owner(Base):
    __tablename__ = 'rto'
    reg_no = Column(Integer, primary_key =  True)
    rto = Column(String)
    state = Column(String)
    owner = Column(String)
    phone = Column(String)
    email = Column(String)
    dt_reg = Column(Date)
    reg_valid_till = Column(Date)
    ins_valid_till = Column(Date)
    puc_valid_till = Column(Date)