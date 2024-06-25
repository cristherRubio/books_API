import requests
import pandas as pd


BASE_URL = "http://127.0.0.1:8000"

def main():
    df = pd.read_csv(r'C:\Users\cris\Downloads\archive\books.csv', delimiter=',', on_bad_lines='skip', encoding='utf-8')
    df.authors = df.authors.str.split('/').str[0]
    print(df.columns)

    for index, row in df.iterrows():
        isbn13 = str(row['isbn13'])
        book_data = {
            'title': {'title': row['title']},
            'author': {'name': row['authors']},
            'editorial': {'name': row['publisher']},
            'isbn': {'isbn_code': isbn13[:3] + '-' + isbn13[3:]}
        }

        #print(book_data)
        add_book(book_data)


def add_book(book):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/books/", json=book, headers=headers)
    if response.status_code == 201:
        print(f"Successfully added book: {book['title']}")
    else:
        try:
            error_message = response.json()
        except requests.exceptions.JSONDecodeError:
            error_message = response.text
        print(f"Failed to add book: {book['title']}. Status code: {response.status_code}, Error: {error_message}")


if __name__ == '__main__':
    main()