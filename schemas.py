from pydantic import BaseModel
from typing import List, Optional

class ISBNSchema(BaseModel):
    isbn_code: str

class EditorialSchema(BaseModel):
    name: str

class BookCreateSchema(BaseModel):
    title: str
    author: str
    editorial: EditorialSchema
    isbn: ISBNSchema

class BookSchema(BaseModel):
    id: int
    title: str
    author: str
    editorials: List[EditorialSchema]
    isbn: Optional[ISBNSchema]

    class Config:
        orm_mode = True

class AuthorSchema(BaseModel):
    id: int
    name: str
    books: List[BookSchema]

    class Config:
        orm_mode = True
