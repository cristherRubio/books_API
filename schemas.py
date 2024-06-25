from pydantic import BaseModel, Field, validator, constr, ValidationError
from typing import List
import re


ALPHANUM_REGEX = r'^[\w!@#$%^&*()-]+(?: [\w!@#$%^&*()-]+)*$'  # Validation for book title
ALPHA_REGEX = r'^[A-Za-z]+(?: [A-Za-z]+)*$'  # Validation for author title
ISBN_REGEX = r'^\d{3}-\d{10}$'  # Validation for ISBN

class ISBN(BaseModel):
    isbn_code: constr(strip_whitespace=True)

    @validator('isbn_code')
    def check_format(cls, value):
        if not re.match(ISBN_REGEX, value):
            raise ValidationError('Invalid ISBN format. Expected format: "###-##########"')
        return value


class Editorial(BaseModel):
    name: constr(strip_whitespace=True)

    @validator('name')
    def check_format(cls, value):
        if not re.match(ALPHANUM_REGEX, value):
            raise ValidationError('Invalid editorial name. Expected format examples: "Simon & Schuster" or "HarperCollins"')
        return value


class Book(BaseModel):
    title: constr(strip_whitespace=True)

    @validator('title')
    def check_format(cls, value):
        if not re.match(ALPHANUM_REGEX, value):
            raise ValidationError('Invalid book name. Expected format: "Crime & Punishment"')
        return value


class Author(BaseModel):
    name: constr(min_length=3, strip_whitespace=True)

    @validator('name')
    def check_format(cls, value):
        if not re.match(ALPHANUM_REGEX, value):
            raise ValidationError('Invalid author name. Expected format: "Arthur Conan Doyle"')
        elif '  ' in value:
            raise ValidationError('Author name should not have double spaces between words')
        return value


class BookCreate(BaseModel):

    model_config = {
        "extra": "forbid",
    }

    title: Book
    author: Author
    editorial: Editorial
    isbn: ISBN


class BookResp(BaseModel):

    model_config = {
        "extra": "forbid",
    }

    title: str
    author: str
    editorials: List[str]
    isbn: str