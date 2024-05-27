import json
from flask import Flask, request, jsonify

app = Flask(__name__)


class bookStore:
    def __init__(self):
        self.books = []
        self.bookGenre = ['SCI_FI', 'NOVEL', 'HISTORY', 'MANGA', 'ROMANCE', 'PROFESSIONAL']
        self.booksNumber = 0

    def findBook(self, filter: dict):
        res = self.books
        if filter.get('genres') is not None:
            for genre in filter['genres'].split(","):
                if genre not in self.bookGenre:
                    return -1

        for argument in filter.keys():
            if argument == "author":
                res = [book for book in res if (book.Author).lower() == (filter["author"]).lower()]
            elif argument == "price-bigger-than":
                res = [book for book in res if book.Price > int(filter["price-bigger-than"])]
            elif argument == "price-less-than":
                res = [book for book in res if book.Price < int(filter["price-less-than"])]
            elif argument =="year-bigger-than":
                res = [book for book in res if book.PrintYear > int(filter["year-bigger-than"])]
            elif argument == "year-less-than":
                res = [book for book in res if book.PrintYear < int(filter["year-less-than"])]
            elif argument == "genres":
                temp =[]
                for book in res:
                    for kind in book.Genre:
                        if kind in filter["genres"].split(","):
                                temp.append(book)
                                continue
                res = temp

        return res

    def addBook(self,book):
        self.books.append(book)
        self.booksNumber += 1

    def validYear(self, year):
        if (1940 <= year <= 2100):
            return True
        else:
            return False

    def checkPrice(self, price):
        if (price > 0):
            return True
        else:
            return False

    def isBookExists(self, bookName):
        if any(bookName.lower() == book.Title.lower() for book in self.books):
            return True
        else:
            return False


class book:
    def __init__(self, id, title, author, year, price, genre):
        self.Id = id
        self.Title = title
        self.Author = author
        self.PrintYear = year
        self.Price = price
        self.Genre = genre

    def to_json(self):
        return {
            "id": self.Id,
            "title": self.Title,
            "author": self.Author,
            "price": self.Price,
            "year": self.PrintYear,
            "genres": json.dumps(self.Genre)
        }
bookStore = bookStore()


@app.route('/books/health', methods=['GET'], endpoint='health')
def Health():
    return 'OK', 200


@app.route('/book', methods=['POST'], endpoint='CreatNewBook')
def CreatNewBook():
    data = request.get_json()
    if (bookStore.isBookExists(data['title'])):
        error = f"Error: Book with the title [{data['title']}] already exists in the system"
        response = jsonify({"errorMessage": error})
        return response, 409

    elif (not bookStore.validYear(data['year'])):
        error = f"Error: Can’t create new Book that its year [{data['year']}] is not in the accepted range [1940 -> 2100]"
        response = jsonify({"errorMessage": error})
        return response, 409

    elif (not bookStore.checkPrice(data['price'])):
        error = f"Error: Can’t create new Book with negative price"
        response = jsonify({"errorMessage": error})
        return response, 409

    else:
        newBook = book(bookStore.booksNumber + 1, data['title'], data['author'], data['year'], data['price'], data['genres'])
        bookStore.addBook(newBook)
        response = jsonify({"result": bookStore.booksNumber})
        return response, 200

@app.route('/books/total', methods=['GET'], endpoint='getTotalBooks')
def getTotalBooks():
    query_params = dict(request.args)
    numOfBooks = bookStore.findBook(query_params)
    if (numOfBooks == -1):
        return '', 400
    else:
        return jsonify({"result": len(numOfBooks)}), 200


@app.route('/books', methods=['GET'], endpoint='getBooksData')
def getBooksData():
    query_params = dict(request.args)
    books = bookStore.findBook(query_params)
    if(books == -1):
        empty_array = []
        return jsonify({"result": json.dumps(empty_array)}), 200
    sorted_books = sorted(books, key=lambda x: x.Title)
    sorted_books_json = [book_obj.to_json() for book_obj in sorted_books]
    return jsonify({"result": sorted_books_json}), 200

@app.route('/book', methods=['GET'], endpoint='getSingleBookData')
def getBookData():
    id_param = int(request.args.get('id'))
    for book in bookStore.books:
        if book.Id == id_param:
            return jsonify({"result": book.to_json()}), 200
    return jsonify({"errorMessage": f"Error: no such Book with id {id_param}"}), 404


@app.route('/book', methods=['PUT'], endpoint='updateBookprice')
def updateBookData():
    id_param = int(request.args.get('id'))
    if id_param <= 0:
        return jsonify({"errorMessage": f"Error: price update for book [{id_param}] must be a positive integer"}), 409
    for book in bookStore.books:
        if book.Id == id_param:
            oldPrice = book.Price
            book.Price = int(request.args.get('price'))
            return jsonify({"result": oldPrice}), 200
    return jsonify({"errorMessage": f"Error: no such Book with id {id_param}"}), 404


@app.route('/book', methods=['DELETE'], endpoint='deleteBook')
def deleteBookData():
    id_param = int(request.args.get('id'))
    for book in bookStore.books:
        if book.Id == id_param:
            bookStore.books.remove(book)
            return jsonify({"result": len(bookStore.books)}), 200
    return jsonify({"errorMessage": f"Error: no such Book with id {id_param}"}), 404

if __name__ == '__main__':
    app.run(debug=False, port=8574)
