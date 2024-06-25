from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# many-to-many association table
book_editorial = Table('book_editorial', Base.metadata,
    Column('book_id', ForeignKey('books.id', ondelete="CASCADE"), primary_key=True),
    Column('editorial_id', ForeignKey('editorials.id', ondelete="CASCADE"), primary_key=True)
)

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    books = relationship("Book", back_populates="author", cascade="all, delete")

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id', ondelete="CASCADE"))
    author = relationship("Author", back_populates="books")
    editorials = relationship("Editorial", secondary=book_editorial, back_populates="books", cascade="all, delete")
    isbn = relationship("ISBN", back_populates="book", uselist=False, cascade="all, delete")

class Editorial(Base):
    __tablename__ = 'editorials'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    books = relationship("Book", secondary=book_editorial, back_populates="editorials", cascade="all, delete")

class ISBN(Base):
    __tablename__ = 'isbns'
    id = Column(Integer, primary_key=True, index=True)
    isbn_code = Column(String, unique=True, nullable=False)
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"))
    book = relationship("Book", back_populates="isbn")