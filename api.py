from flask import Flask, jsonify, request, send_file
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# PostgreSQL konekcija
DB_CONFIG = {
    'dbname': 'labos',
    'user': 'postgres',
    'password': 'lozinka',
    'host': 'localhost',
    'port': 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# GET - Dohvati sve podatke
@app.route('/podaci', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""SELECT books.*, authors.name, authors.surname 
                  FROM books
                  JOIN authors ON books.author_id = authors.author_id""")
        data = cur.fetchall()
        cur.close()
        conn.close()

        jsonld_data = [
            {
                "@context": "https://schema.org/",
                "@type": "Book",
                "name": item['title'],
                "author": {
                    "@type": "Person",
                    "name": f"{item['name']} {item['surname']}"
                },
                "datePublished": item['year_of_original_publication'],
                "isbn": item['isbn13'],
                "publisher": item['publisher'],
                "numberOfPages": item['num_of_pages'],
                "inLanguage": item['language'],
                "isPartOf": {
                    "@type": "CreativeWorkSeries",
                    "name": item['series'] if item['series'] else None
                },
                "genre": item['genres']
            }
            for item in data
        ]
        
        return jsonify({"status": "OK", "message": "Fetched all entries", "response": jsonld_data}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

# GET - Dohvati pojedinačni zapis
@app.route('/podaci/<string:id>', methods=['GET'])
def get_record(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""SELECT books.*, authors.name, authors.surname 
                  FROM books
                  JOIN authors ON books.author_id = authors.author_id
                  WHERE books.isbn13 = %s""", (id,))
        record = cur.fetchone()
        cur.close()
        conn.close()

        if record:
            jsonld_item = {
                "@context": "https://schema.org/",
                "@type": "Book",
                "name": record['title'],
                "author": {
                    "@type": "Person",
                    "name": f"{record['name']} {record['surname']}"
                },
                "datePublished": record['year_of_original_publication'],
                "isbn": record['isbn13'],
                "publisher": record['publisher'],
                "numberOfPages": record['num_of_pages'],
                "inLanguage": record['language'],
                "isPartOf": {
                    "@type": "CreativeWorkSeries",
                    "name": record['series'] if record['series'] else None
                },
                "genre": record['genres']
            }
            return jsonify({"status": "OK", "message": "Fetched entry with corresponding isbn13", "response": jsonld_item}), 200
        return jsonify({"status": "Not Found", "message": "Book with the provided ISBN13 doesn't exist", "response": "null"}), 404
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

# GET - dohvati knjige po naslovu
@app.route('/podaci/pretraga', methods=['GET'])
def search_books():
    try:
        naslov = request.args.get('naslov', '')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT books.*, authors.name, authors.surname FROM books JOIN authors ON books.author_id = authors.author_id WHERE books.title ILIKE %s", (f'%{naslov}%',))
        records = cur.fetchall()
        cur.close()
        conn.close()

        jsonld_data = [
            {
                "@context": "https://schema.org/",
                "@type": "Book",
                "name": item['title'],
                "author": {
                    "@type": "Person",
                    "name": f"{item['name']} {item['surname']}"
                },
                "datePublished": item['year_of_original_publication'],
                "isbn": item['isbn13'],
                "publisher": item['publisher'],
                "numberOfPages": item['num_of_pages'],
                "inLanguage": item['language'],
                "isPartOf": {
                    "@type": "CreativeWorkSeries",
                    "name": item['series'] if item['series'] else None
                },
                "genre": item['genres']
            }
            for item in records
        ]

        return jsonify({"status": "OK", "message": "Books matching search criteria", "response": jsonld_data}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    
# GET - dohvati knjige po imenu i prezimenu autora
@app.route('/podaci/autor', methods=['GET'])
def get_books_by_author():
    try:
        ime = request.args.get('ime', '')
        prezime = request.args.get('prezime', '')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT books.*, authors.name, authors.surname 
            FROM books 
            JOIN authors ON books.author_id = authors.author_id 
            WHERE authors.name ILIKE %s AND authors.surname ILIKE %s
        """, (f'%{ime}%', f'%{prezime}%'))
        records = cur.fetchall()
        cur.close()
        conn.close()

        jsonld_data = [
            {
                "@context": "https://schema.org/",
                "@type": "Book",
                "name": item['title'],
                "author": {
                    "@type": "Person",
                    "name": f"{item['name']} {item['surname']}"
                },
                "datePublished": item['year_of_original_publication'],
                "isbn": item['isbn13'],
                "publisher": item['publisher'],
                "numberOfPages": item['num_of_pages'],
                "inLanguage": item['language'],
                "isPartOf": {
                    "@type": "CreativeWorkSeries",
                    "name": item['series'] if item['series'] else None
                },
                "genre": item['genres']
            }
            for item in records
        ]

        return jsonify({"status": "OK", "message": "Books by specified author", "response": jsonld_data}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

# GET - dohvati knjige po žanru
@app.route('/podaci/genre/<string:genre>', methods=['GET'])
def get_books_by_genre(genre):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT books.*, authors.name, authors.surname 
            FROM books 
            JOIN authors ON books.author_id = authors.author_id 
            WHERE %s = ANY (books.genres)
        """, (genre,))
        records = cur.fetchall()
        cur.close()
        conn.close()
        if records:
            
             jsonld_data = [
                 {
                     "@context": "https://schema.org/",
                     "@type": "Book",
                     "name": item['title'],
                     "author": {
                         "@type": "Person",
                         "name": f"{item['name']} {item['surname']}"
                     },
                     "datePublished": item['year_of_original_publication'],
                     "isbn": item['isbn13'],
                     "publisher": item['publisher'],
                     "numberOfPages": item['num_of_pages'],
                     "inLanguage": item['language'],
                     "isPartOf": {
                         "@type": "CreativeWorkSeries",
                         "name": item['series'] if item['series'] else None
                     },
                     "genre": item['genres']
                 }
                 for item in records
             ]

             return jsonify({"status": "OK", "message": f"Books with genre {genre}", "response": jsonld_data}), 200
        return jsonify({"status": "Not Found", "message": f"No books found with genre {genre}", "response": []}), 404
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

# POST - Dodaj novi zapis
@app.route('/podaci', methods=['POST'])
def add_record():
   try:
      new_record = request.json
      print(new_record)
      if 'autor' in new_record and isinstance(new_record['autor'], list) and len(new_record['autor']) > 0:
         authorName = new_record['autor'][0].get('name', None)
         authorSurname = new_record['autor'][0].get('surname', None)
      else:
         return jsonify({"status": "Error", "message": "No author information found."}), 404

      conn = get_db_connection()
      cur = conn.cursor()

      cur.execute("SELECT * FROM books WHERE isbn13 = %s", (new_record['isbn13'],))
      existing_book = cur.fetchone()

      if existing_book:
         return jsonify({"status": "Error", "message": f"Book with ISBN13 {new_record['isbn13']} already exists.", "response": existing_book}), 409

      cur.execute("SELECT author_id FROM authors WHERE name = %s AND surname = %s", (authorName, authorSurname))
      record = cur.fetchone()

      if record:
         authorID = record['author_id'] 
         print(f"Existing author found with ID: {authorID}")
      else:
         cur.execute(
            "INSERT INTO authors (name, surname) VALUES (%s, %s) RETURNING author_id",
            (authorName, authorSurname)
         )
         authorID = cur.fetchone()['author_id']
         conn.commit()
         print(f"New author added with ID: {authorID}")

      cur.execute(
         """
         INSERT INTO books (
            title, year_of_original_publication, year_of_publication, isbn13, isbn10, 
            publisher, num_of_pages, language, series, author_id, genres
         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
         RETURNING *
         """,
         (
            new_record['title'], new_record['year_of_original_publication'], new_record['year_of_publication'],
            new_record['isbn13'], new_record['isbn10'], new_record['publisher'], new_record['num_of_pages'],
            new_record['language'], new_record['series'], authorID, 
            '{' + ','.join(f'"{genre}"' for genre in new_record['genres']) + '}' 
         )
      )
      book_record = cur.fetchone()
      conn.commit()

      print("New book added successfully")

      cur.close()
      conn.close()
      return jsonify(book_record), 200

   except Exception as e:
      return jsonify({"status": "Error", "message": str(e)}), 500



# PUT - Ažuriraj zapis
@app.route('/podaci/<string:id>', methods=['PUT'])
def update_record(id):
   try:
      new_record = request.json
      if id != new_record['isbn13']:
         return jsonify({"status": "Error", "message": "New isbn value different from current one"}), 500
      if 'autor' in new_record and isinstance(new_record['autor'], list) and len(new_record['autor']) > 0:
         authorName = new_record['autor'][0].get('name', None)
         authorSurname = new_record['autor'][0].get('surname', None)
      else:
         return jsonify({"status": "Error", "message": "No author information found."}), 404

      print(authorName)
      print(authorSurname)

      conn = get_db_connection()
      cur = conn.cursor()
      cur.execute("SELECT author_id FROM authors WHERE name = %s AND surname = %s", (authorName, authorSurname))
      record = cur.fetchone()

      if record:
         authorID = record['author_id'] 
         print(f"Existing author found with ID: {authorID}")
      else:
         cur.execute(
            "INSERT INTO authors (name, surname) VALUES (%s, %s) RETURNING author_id",
            (authorName, authorSurname)
         )
         authorID = cur.fetchone()['author_id']
         conn.commit()
         print(f"New author added with ID: {authorID}")
      print(authorID)

      cur.execute("DELETE FROM books WHERE isbn13 = %s RETURNING *", (id,))
      record = cur.fetchone()
      conn.commit()

      cur.execute(
         """
         INSERT INTO books (
            title, year_of_original_publication, year_of_publication, isbn13, isbn10, 
            publisher, num_of_pages, language, series, author_id, genres
         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
         RETURNING *
         """,
         (
            new_record['title'], new_record['year_of_original_publication'], new_record['year_of_publication'],
            new_record['isbn13'], new_record['isbn10'], new_record['publisher'], new_record['num_of_pages'],
            new_record['language'], new_record['series'], authorID, 
            '{' + ','.join(f'"{genre}"' for genre in new_record['genres']) + '}' 
         )
      )
      book_record = cur.fetchone()
      conn.commit()

      cur.close()
      conn.close()
      return jsonify(book_record), 200

   except Exception as e:
      return jsonify({"status": "Error", "message": str(e)}), 500



# DELETE - Izbriši zapis
@app.route('/podaci/<string:id>', methods=['DELETE'])
def delete_record(id):
   try:
      conn = get_db_connection()
      cur = conn.cursor()
      cur.execute("DELETE FROM books WHERE isbn13 = %s RETURNING *", (id,))
      record = cur.fetchone()
      conn.commit()
      cur.close()
      conn.close()

      if record:
         return jsonify({"message": f"Book with ISBN13 {id} deleted"}), 200
      return jsonify({"status": "Not Found", "message": "Book with the provided ISBN13 doesn't exist", "response": "null"}), 404
   except Exception as e:
      return jsonify({"status": "Error", "message": str(e)}), 500

# GET - Vrati openAPI specifikaciju
@app.route('/openapi.json', methods=['GET'])
def get_openapi():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'openapi.json')
        
        return send_file(file_path, mimetype='application/json')
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

# Kod za nepodržane rute
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed", "message": "This method is not implemented"}), 501

if __name__ == '__main__':
    app.run(debug=True)
