from pydantic import BaseModel, Field
import datetime

class BookingCreate(BaseModel):
    user_id: int
    room_id: int
    booking_num: int
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
        
class Booking(BookingCreate):
    booking_id: int
    
    class Config:
        orm_mode = True
    
class UserCreate(BaseModel):
    user_name: str = Field(max_length=20)
        
class User(UserCreate):
    user_id: int
    
    class Config:
        orm_mode = True
    
class RoomCreate(BaseModel):
    room_name: str = Field(max_length=20)
    capacity: int 
        
class Room(RoomCreate):
    room_id: int
    
    class Config:
        orm_mode = True