from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

def get_users(db: Session, skip: int = 0, limit: int =100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_rooms(db: Session, skip: int = 0, limit: int =100):
    return db.query(models.Room).offset(skip).limit(limit).all()

def get_bookings(db: Session, skip: int = 0, limit: int =100):
    return db.query(models.Booking).offset(skip).limit(limit).all()

def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()

def create_user(db: Session, user: schemas.User):
    db_user = models.User(user_name=user.user_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_room(db: Session, room: schemas.Room):
    db_room = models.Room(room_name=room.room_name, capacity=room.capacity)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def create_booking(db: Session, booking: schemas.Booking):
    db_booked = db.query(models.Booking).\
                filter(models.Booking.room_id == booking.room_id).\
                filter(models.Booking.start_datetime < booking.end_datetime).\
                filter(models.Booking.end_datetime > booking.start_datetime).\
                all()
                
    if len(db_booked) == 0:
        db_booking = models.Booking(
            user_id = booking.user_id,
            room_id = booking.room_id,
            booking_num = booking.booking_num,
            start_datetime = booking.start_datetime,
            end_datetime = booking.end_datetime
            )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    
    else:
        raise HTTPException(status_code=404, detail="Already booked")
    
def delete_booking(db: Session, already_booked: models.Booking):
    db.delete(already_booked)
    db.commit()
    