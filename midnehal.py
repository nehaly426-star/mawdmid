'''
a1 (b) sqlite3
a2 (b) conn.commit()
a3 (b) 2
a4 (c) None
a5 (c) 5
a6 (b) uvicorn main:app --reload
a7 (a) /swagger
a8 (b) post
a9 (d) 422
a10 (c) 303

'''


#b1
import sqlite3
conn = sqlite3.connect('college.db')
cursor = conn.cursor()
cursor.execute(
    "SELECT name, marks FROM students WHERE marks > ? ORDER BY marks DESC",
    (80,)
)

for name, marks in cursor.fetchall():
    print(name, marks)

conn.commit()
conn.close()


#output-->
#Sneha 92
#Priya 88





#b2
import sqlite3

conn = sqlite3.connect("college.db") 
cur = conn.cursor()

cur.execute(
    "INSERT INTO students (name, course, city, marks) VALUES (?, ?, ?, ?)",
    ("Vikram", "BCA", "Udaipur", 67)
)

conn.commit()  
conn.close()


#Vikram will get id= 6 because there are already 5 students in the table and id column is set to autoincrement.




#b3 crud stands for:
#C= CREATE(operation)= sql(INSERT) and fastapi http method(POST)
#R= READ(operation)= sql(SELECT) and fastapi http method(GET)
#U= UPDATE(operation)= sql(UPDATE) and fastapi http method(PUT)
#D= DELETE(operation)= sql(DELETE) and fastapi http method(DELETE)


#b4
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}

# Example: GET /hello/Aman returns {"message": "Hello Aman"}



#b5 corrected code: + will not be used and student id in bracket
@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,) #corrected line
    ).fetchone()
    conn.close()

    if row is None:
        return {"error": "not found"}
    return dict(row)







#c1
import sqlite3

conn = sqlite3.connect("library.db")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        price REAL
    )
""")

books = [
    ("Python Basics", "Rao", 250),
    ("SQL Guide", "Mehta", 180),
    ("Web Dev", "Khan", 400),
]

cur.executemany(
    "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
    books
)

cur.execute(
    "UPDATE books SET price = price * 1.10 WHERE id = ?",
    (2,)
)
print("Rows updated:", cur.rowcount)

cur.execute("DELETE FROM books WHERE price < ?", (200,))
conn.commit()

print("Remaining books:")
cur.execute("SELECT id, title, author, price FROM books ORDER BY id")
for book in cur.fetchall():
    print(book)

conn.close()



'''
output-->
Rows updated: 1
Remaining books:
(1, 'Python Basics', 'Rao', 250.0)
(3, 'Web Dev', 'Khan', 400.0)
'''








#c2

import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
DATABASE = "shop.db"


class Book(BaseModel):
    title: str
    author: str
    price: float


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


#create the table if it does not already exist.
with get_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            price REAL
        )
    """)


@app.post("/books", status_code=201)
def create_book(book: Book):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
            (book.title, book.author, book.price),
        )
        row = conn.execute(
            "SELECT * FROM books WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


@app.get("/books")
def get_books():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM books ORDER BY id").fetchall()
        return [dict(row) for row in rows]


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return dict(row)


@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Book not found")

        conn.execute(
            "UPDATE books SET title = ?, author = ?, price = ? WHERE id = ?",
            (book.title, book.author, book.price, book_id),
        )
        updated = conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        return dict(updated)


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")

    return {"message": "Book deleted"}


#run it with uvicorn main:app --reload