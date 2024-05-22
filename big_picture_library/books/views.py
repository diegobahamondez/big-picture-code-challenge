import json
import requests

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Book

#there are several methods for validating ISBN, including creating your own algorithms. But from what
#I've learned I can say: The less code you have to mantain, the better for the project.
#I also checked the github of this library and performs well without any issues.
from isbnlib import is_isbn10, is_isbn13 

@require_http_methods(["GET"])
def fetch_book_details(request, isbn):

    # validate isbn
    if not (is_isbn10(isbn) or is_isbn13(isbn)):
        return JsonResponse({"error": "Invalid ISBN"}, status=400)

    #get response from the openlibrary api
    response = requests.get(f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json")
    if response.status_code != 200:
        return JsonResponse({"error": "Book not found"}, status=404)

    data = response.json()
    if 'records' not in data or not data['records']:
        return JsonResponse({"error": "Book not found"}, status=404)
    
    book_data = list(data['records'].values())[0]['data']
    book_details = {
        "isbn": isbn,
        "title": book_data.get("title"),
        "author": book_data.get("authors", [{}])[0].get("name", "Unknown Author"),
        "summary": book_data.get("notes", ""),
        "cover_url": book_data.get("cover", {}).get("medium", "")
    }

    return JsonResponse(book_details)

#decided to use a class based view here for better scalability, eg: adding more http methods to the book view
@method_decorator(csrf_exempt, name='dispatch')
class BookView(View):
    
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        isbn = body.get("isbn")
        if not isbn:
            return JsonResponse({"error": "ISBN is required"}, status=400)

        if not (is_isbn10(isbn) or is_isbn13(isbn)):
            return JsonResponse({"error": "Invalid ISBN"}, status=400)

        response = requests.get(f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json")
        if response.status_code != 200:
            return JsonResponse({"error": "Book not found"}, status=404)

        data = response.json()
        if 'records' not in data or not data['records']:
            return JsonResponse({"error": "Book not found"}, status=404)

        book_data = list(data['records'].values())[0]['data']
        book, created = Book.objects.update_or_create(
            isbn=isbn,
            defaults={
                "title": book_data.get("title"),
                "author": book_data.get("authors", [{}])[0].get("name", "Unknown Author"),
                "summary": book_data.get("notes", ""),
                "cover_url": book_data.get("cover", {}).get("medium", "")
            }
        )

        return JsonResponse({
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "summary": book.summary,
            "cover_url": book.cover_url
        }, status=201 if created else 200)
    
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().values("isbn", "title", "author", "summary", "cover_url")
        return JsonResponse(list(books), safe=False)
