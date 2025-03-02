# from imp import reload
import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from fastapi.responses import JSONResponse
import sqlalchemy
from sqlalchemy.orm import Session
from fastapi import Depends
#  127.0.0.1:5432
# "user: postgres, localhost : 5432 , newpassword"

# Database connection details
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:newpassword@localhost/Players"

# Create the engine to connect to PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Base class for SQLAlchemy models
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    published_date = Column(Date)

# Create the database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic model to handle request and response data
class BookCreate(BaseModel):
    id: int
    title: str
    author: str
    published_date: date

class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True  # This allows the conversion from ORM model to Pydantic model

# FastAPI app
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# from . import app

# Create a new book
@app.post("/books/", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    try:
        db_book = Book(id=book.id, title=book.title, author=book.author, published_date=book.published_date)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        print("dbbook :",db_book)
        return db_book
    except Exception as err:
        # print("dbbook :", db_book)
        data = {"error in create" : err.args[0]}
        # return JSONResponse(content=data, status_code=200)
        return {"error in create" : err.args[0]}

# Get all books
@app.get("/books/", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

# Get a book by ID
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# Update an existing book
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = book.title
    db_book.author = book.author
    db_book.published_date = book.published_date
    db.commit()
    db.refresh(db_book)
    return db_book

# Delete a book
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}

print("sdfsddsfg")

if __name__ == "__main__":
    uvicorn.run("app:app")
