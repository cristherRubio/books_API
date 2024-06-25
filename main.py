from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Function to add a new book
@app.post("/books/", status_code=201, response_model=schemas.Book)
def add_book(book_data: schemas.BookCreate, db: Session = Depends(database.get_db)):
    try:
        # Check if author exists or create a new one
        author = db.query(models.Author).filter(models.Author.name.ilike(f"%{book_data.author.name}%")).first()
        if not author:
            author = models.Author(name=book_data.author.name)
            db.add(author)
            db.commit()
            db.refresh(author)
        
        # Create the book with its ISBN together
        new_book = models.Book(title=book_data.title.title, author_id=author.id)
        
        # Check if ISBN already exists
        isbn = db.query(models.ISBN).filter(models.ISBN.isbn_code == book_data.isbn.isbn_code).first()
        if isbn:
            if isbn.book.title != new_book.title:
                print('isbn ERROR')
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Existing ISBN for different title: ' + str(e))
        else:
            isbn = models.ISBN(isbn_code=book_data.isbn.isbn_code)

        new_book.isbn = isbn

        # Check if a book with the same title and ISBN already exists
        existing_book = db.query(models.Book).filter(
            models.Book.title == book_data.title.title,
            models.Book.isbn.has(isbn_code=book_data.isbn.isbn_code)).first()

        # Check if editorial exists or create new ones and associate with the book
        editorial = db.query(models.Editorial).filter(models.Editorial.name.ilike(f"%{book_data.editorial.name}%")).first()
        if not editorial:
            editorial = models.Editorial(name=book_data.editorial.name)
            db.add(editorial)
            db.commit()
            db.refresh(editorial)
        # Add editorial to the book
        new_book.editorials.append(editorial)

        # Handle the existing book case
        if existing_book:
            if any(ed.name == book_data.editorial.name for ed in existing_book.editorials):
                print('duplicate ERROR')
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This book with the same editorial already exists.')
            # Add new editorial to the existing book
            existing_book.editorials.append(editorial)
            db.commit()
            db.refresh(existing_book)
            return existing_book
        else:
            # Create a new book
            new_book = models.Book(title=book_data.title.title, author_id=author.id)
            new_book.isbn = isbn
            new_book.editorials.append(editorial)
            
            # Add the new book to the database
            db.add(new_book)
            db.commit()
            db.refresh(new_book)
            return new_book
    
    except Exception as e:
        db.rollback()  # Rollback changes if any exception occurs
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Rollback: ' + str(e))


# Endpoint to read books by book like(title)
@app.get("/book/{book_name}", response_model=List[schemas.BookResp])
def read_books(book_name: str, skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    # Query books filtered by book title (assuming book_name matches the title)
    books = db.query(models.Book).filter(models.Book.title.ilike(f"%{book_name}%")).offset(skip).limit(limit).all()
    # Prepare response data
    book_resp_list = []
    for book in books:
        editorials = [editorial.name for editorial in book.editorials]        
        # Construct BookResp object
        book_resp = schemas.BookResp(
            title=book.title,
            author=book.author.name,
            editorials=editorials,
            isbn=book.isbn.isbn_code
        )
        book_resp_list.append(book_resp)
    
    return book_resp_list


# Endpoint to read a book by ISBN
@app.get("/isbn/{isbn}", response_model=schemas.BookResp)
def read_book_by_isbn(isbn: str, db: Session = Depends(database.get_db)):
    isbn_entry = db.query(models.ISBN).filter(models.ISBN.isbn_code == isbn).first()
    if not isbn_entry:
        raise HTTPException(status_code=404, detail="ISBN not found")
    
    book = db.query(models.Book).filter(models.Book.id == isbn_entry.book_id).first()
    editorials = [editorial.name for editorial in book.editorials]
    
    book_resp = schemas.BookResp(
        title=book.title,
        author=book.author.name,
        editorials=editorials,
        isbn=book.isbn.isbn_code
    )
    
    return book_resp