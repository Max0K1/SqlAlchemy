from flask import Flask, request, jsonify
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Налаштування Flask
app = Flask(__name__)

# Налаштування SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///library.db')
Session = sessionmaker(bind=engine)
session = Session()

# Моделі SQLAlchemy
class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    books = relationship('Book', back_populates='author', cascade='all, delete-orphan')

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    author = relationship('Author', back_populates='books')

# Створення таблиць
Base.metadata.create_all(engine)

# Обробник для кореневого маршруту
@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Authors and Books API!"}, 200

# Маршрути для роботи з авторами
@app.route("/authors", methods=["GET"])
def list_authors():
    authors = session.query(Author).all()
    return jsonify([{"id": author.id, "name": author.name} for author in authors])

@app.route("/authors", methods=["POST"])
def create_author():
    data = request.get_json()
    if not data or "name" not in data:
        return {"message": "Invalid data, 'name' is required"}, 400

    new_author = Author(name=data["name"])
    session.add(new_author)
    session.commit()
    return {"message": f"Author '{data['name']}' created successfully."}, 201

@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    author = session.query(Author).get(author_id)
    if author:
        session.delete(author)
        session.commit()
        return {"message": f"Author with ID {author_id} deleted."}
    else:
        return {"message": f"Author with ID {author_id} not found."}, 404

@app.route("/authors/<int:author_id>", methods=["GET"])
def get_author_by_id(author_id):
    author = session.query(Author).get(author_id)
    if author:
        return {
            "id": author.id,
            "name": author.name,
            "books": [{"id": book.id, "title": book.title} for book in author.books]
        }
    else:
        return {"message": f"Author with ID {author_id} not found."}, 404

@app.route("/authors_with_books", methods=["POST"])
def add_author_with_books():
    data = request.get_json()
    if not data or "name" not in data or "books" not in data:
        return {"message": "Invalid data, 'name' and 'books' are required"}, 400

    new_author = Author(name=data["name"])
    new_author.books = [Book(title=book_title) for book_title in data["books"]]
    session.add(new_author)
    session.commit()
    return {"message": f"Author '{data['name']}' with books added successfully."}, 201

@app.route("/authors/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    data = request.get_json()
    if not data or "name" not in data:
        return {"message": "Invalid data, 'name' is required"}, 400

    author = session.query(Author).get(author_id)
    if not author:
        return {"message": f"Author with ID {author_id} not found."}, 404

    author.name = data["name"]
    session.commit()
    return {"message": f"Author with ID {author_id} updated successfully."}, 200

# Маршрути для роботи з книгами
@app.route("/books", methods=["GET"])
def list_books():
    books = session.query(Book).all()
    return jsonify([{"id": book.id, "title": book.title, "author_id": book.author_id} for book in books])

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    if not data or "title" not in data or "author_id" not in data:
        return {"message": "Invalid data, 'title' and 'author_id' are required"}, 400

    author = session.query(Author).get(data["author_id"])
    if not author:
        return {"message": f"Author with ID {data['author_id']} not found."}, 404

    new_book = Book(title=data["title"], author=author)
    session.add(new_book)
    session.commit()
    return {"message": f"Book '{data['title']}' created successfully."}, 201

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = session.query(Book).get(book_id)
    if book:
        session.delete(book)
        session.commit()
        return {"message": f"Book with ID {book_id} deleted."}
    else:
        return {"message": f"Book with ID {book_id} not found."}, 404

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
    book = session.query(Book).get(book_id)
    if book:
        return {
            "id": book.id,
            "title": book.title,
            "author": {"id": book.author.id, "name": book.author.name}
        }
    else:
        return {"message": f"Book with ID {book_id} not found."}, 404

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json()
    if not data:
        return {"message": "Invalid data, 'title' or 'author_id' is required"}, 400

    book = session.query(Book).get(book_id)
    if not book:
        return {"message": f"Book with ID {book_id} not found."}, 404

    if "title" in data:
        book.title = data["title"]

    if "author_id" in data:
        author = session.query(Author).get(data["author_id"])
        if not author:
            return {"message": f"Author with ID {data['author_id']} not found."}, 404
        book.author = author

    session.commit()
    return {"message": f"Book with ID {book_id} updated successfully."}, 200

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True)