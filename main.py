from fastapi import FastAPI
#from enum import Enum
from typing import Optional

app = FastAPI()

BOOKS={
    'book_1':{'title':'Title One','author':'Author One'},
    'book_2':{'title':'Title Two','author':'Author Two'},
    'book_3':{'title':'Title Three','author':'Author Three'},
    'book_4':{'title':'Title Four','author':'Author Four'},
    'book_5':{'title':'Title Five','author':'Author Five'},
}


@app.get("/")
#async def readAllBooks(skipBook:str ="book_3"):
async def readAllBooks(skipBook:Optional[str] = None):
    newBooks = BOOKS.copy()
    if skipBook:
        del newBooks[skipBook]
    return newBooks

@app.get("/{bookName}")
async def readBookByName(bookName:str):
    return BOOKS[bookName]

@app.get("/book/mybook")
async def read_favourite_book():
    return {"book_title":"My Favourite book"}

@app.get("/book/{bookTitle}")
async def readBook(bookTitle:str):
    return {"book_title" : bookTitle}


@app.post("/")
async def createBook(book_title:str, book_author:str):
    current_book_id = 0
    for book in BOOKS:
        x = int(book.split('_')[-1])
        if x > current_book_id:
           current_book_id = x

    BOOKS[f'book_{current_book_id+1}'] = {'Title':book_title, 'Author':book_author}
    return BOOKS[f'book_{current_book_id+1}']

@app.put("/{bookName}")
async def updateBook(bookName:str, bookTitle:str, bookAuthor:str):
    try:
        if BOOKS[bookName]:
            bookInformation = {"Title": bookTitle,"Author":bookAuthor}
            BOOKS[bookName] = bookInformation
            return bookInformation
    except:
        return f"No book found to update"

@app.delete("/{bookName}")
async def deleteBook(bookName:str):
    del BOOKS[bookName]
    return f'Book {bookName} deleted'

'''

class Direction(str,Enum):
    north="North"
    south="South"
    east="East"
    west="West"

@app.get("/direction/{directionName}")
async def getDirection(directionName:Direction):
    if directionName == Direction.north:
        return {"Direction" : directionName ,"sub":"Up"}
    elif directionName == Direction.south:
        return {"Direction" : directionName ,"sub":"Down"}
    elif directionName == Direction.east:
        return {"Direction" : directionName ,"sub":"Right"}

    return {"Direction" : directionName ,"sub":"Left"}

'''
