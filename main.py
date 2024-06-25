from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Function to add a new book
@app.post("/books/", response_model=schemas.Book)
def add_book(book_data: schemas.BookCreate, db: Session = Depends(database.get_db)):
    # Check if author already exists or create a new one
    author = db.query(models.Author).filter(models.Author.name == book_data.author).first()
    if not author:
        author = models.Author(name=book_data.author)
        db.add(author)
        db.commit()
        db.refresh(author)
    
    # Check if editorial already exists or create a new one
    editorial = db.query(models.Editorial).filter(models.Editorial.name == book_data.editorial.name).first()
    if not editorial:
        editorial = models.Editorial(name=book_data.editorial.name)
        db.add(editorial)
        db.commit()
        db.refresh(editorial)
    
    # Check if ISBN already exists or create a new one
    isbn = db.query(models.ISBN).filter(models.ISBN.isbn_code == book_data.isbn.isbn_code).first()
    if not isbn:
        isbn = models.ISBN(isbn_code=book_data.isbn.isbn_code)
        db.add(isbn)
        db.commit()
        db.refresh(isbn)
    
    # Create the book
    new_book = models.Book(title=book_data.title, author_id=author.id, editorial_id=editorial.id, isbn_id=isbn.id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book

# Endpoint to read books
@app.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books
