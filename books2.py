from  fastapi import FastAPI, HTTPException, Request, status,Form,Header
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from starlette.responses import JSONResponse

app = FastAPI()

class NegativeNumberException(Exception):
    def __init__(self,booksToReturn):
        self.booksToReturn=booksToReturn

class Book(BaseModel):
    id:UUID
    title:str = Field(min_length=1)
    author:str=Field(min_length=1, max_length=100)
    description:Optional[str] = Field(title="Description of the book",max_length=100, min_length=1)
    rating:int = Field(gt=-1,le=100)
    class Config:
        schema_extra={
            "example":{
                "id":"5b1a593a-1348-41d4-ab7b-35fdf5928a0f",
                "title":"Electronics with Omkar",
                "author":"Omkar",
                "description":"THoughtful book",
                "rating":30
            }
        }

class BookNoRating(BaseModel):
    id:UUID
    title:str = Field(min_length=1)
    author:str=Field(min_length=1, max_length=100)
    description:Optional[str] = Field(title="Description of the book",max_length=100, min_length=1)

BOOKS = []

@app.exception_handler(NegativeNumberException)
async def NegativeNumberExceptionHandler(request:Request, exception:NegativeNumberException):
    print('request', request)
    return JSONResponse(status_code=418,content={"message": f"Invalid number of books {exception.booksToReturn} requested" })

@app.get("/")
async def readAllBooks(booksToReturn:Optional[int] = None):
    if booksToReturn and booksToReturn < 0:
        raise NegativeNumberException(booksToReturn)
    if len(BOOKS)<1:
        createBookNoAPI()
    if booksToReturn and len(BOOKS)> booksToReturn >= 1:
        i=1
        newBooks=[]
        while i <= booksToReturn:
            newBooks.append(BOOKS[i-1])
            i+=1
        return newBooks
    return BOOKS

@app.get("/book/{bookId}")
async def readBook(bookId:UUID):
    for book in BOOKS:
        if book.id == bookId:
            return book
    raise raiseNoBookFoundException()

@app.get("/book/rating/{bookId}",response_model= BookNoRating)
async def readBookNoRating(bookId:UUID):
    for book in BOOKS:
        if book.id == bookId:
            return book
    raise raiseNoBookFoundException()

@app.delete("/{bookId}")
async def deleteBook(bookId:UUID ):
    count=0
    for book in BOOKS:
        if book.id == bookId:
            deleteBook= BOOKS[count]
            del BOOKS[count] 
            print (f"Book of id {bookId} deleted")
            return deleteBook
        count += 1
    raise raiseNoBookFoundException()

@app.put("/{bookId}")
async def updateBook(bookId:UUID,bookUpdate:Book ):
    count=0
    for book in BOOKS:
        if book.id == bookId:
            BOOKS[count] = bookUpdate
            return BOOKS[count]
        count += 1
    raise raiseNoBookFoundException()

@app.post("/",status_code=status.HTTP_201_CREATED)
async def createbook(book :Book):
    BOOKS.append(book)
    return book

@app.post("/books/login")
async def bookLogin(bookToRead:int,username:Optional[str] = Header(None), password:Optional[str]=Header(None)):
    if username=="FastAPI" and password=="test1234!":
        return BOOKS[bookToReadUUID]
    else:
        return JSONResponse(status_code=413,content={"message":"Invalid User"})

@app.get("/header")
async def readHeader(randomHeader:Optional[str]=Header(None)):
    return {"randomHeader":randomHeader}


def createBookNoAPI():
    book1= Book(id="5b1a593a-1348-41d4-ab7b-35fdf5928a0f",title="Book1",description="My book1"
                    ,author="Author1",rating = 40);
    book2= Book(id="4b1a593a-1348-41d4-ab7b-35fdf5928a0f",title="Book2",description="My book2"
                    ,author="Author2",rating = 40);
    book3= Book(id="3b1a593a-1348-41d4-ab7b-35fdf5928a0f",title="Book3",description="My book3"
                    ,author="Author3",rating = 80);
    book4= Book(id="2b1a593a-1348-41d4-ab7b-35fdf5928a0f",title="Book4",description="My book4"
                    ,author="Author4",rating = 70);
    book5= Book(id="1b1a593a-1348-41d4-ab7b-35fdf5928a0f",title="Book5",description="My book5"
                    ,author="Author5",rating = 90);
    BOOKS.append(book1)
    BOOKS.append(book2)
    BOOKS.append(book3)
    BOOKS.append(book4)
    BOOKS.append(book5)

def raiseNoBookFoundException():
    return HTTPException(status_code=404,detail="Book Not found", headers={"X-Error": "Nothing to be seen at the UUID"})

