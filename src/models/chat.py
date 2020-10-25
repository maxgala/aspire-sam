import enum
from datetime import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum, DateTime
from sqlalchemy.dialects.postgresql import ARRAY

from base import Base, MutableList


class ChatType(enum.Enum):
    ONE_ON_ONE = 1
    FOUR_ON_ONE = 2
    MOCK_INTERVIEW = 3

class ChatStatus(enum.Enum):
    PENDING = 1 # needs approval? not available for reservation yet
    ACTIVE = 2 # can only reserve a chat which is active
    RESERVED = 3 # once booked
    DONE = 4 # ????
    CANCELED = 5 # only through the editchat


credit_mapping = {
    ChatType.ONE_ON_ONE: 5,
    ChatType.FOUR_ON_ONE: 3,
    ChatType.MOCK_INTERVIEW: 5
}

mandatory_date = [
    ChatType.FOUR_ON_ONE,
    ChatType.MOCK_INTERVIEW
]


class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(Integer(), primary_key=True)
    chat_type = Column(Enum(ChatType), nullable=False)
    description = Column(String(255))
    tags = Column(MutableList.as_mutable(ARRAY(String(100)))) #need to filter by these
    credits = Column(Integer(), nullable=False)
    chat_status = Column(Enum(ChatStatus), nullable=False)
    aspiring_professionals = Column(MutableList.as_mutable(ARRAY(String(100))))
    senior_executive = Column(String(100), nullable=False)
    date = Column(DateTime())
    end_date = Column(DateTime())

    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
