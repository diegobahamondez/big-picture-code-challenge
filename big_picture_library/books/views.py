import json
import requests

#there are several methods for validating ISBN, including creating your own algorithms. But from what
#I've learned I can say: The less code you have to mantain, the better for the project.
#I also checked the github of this library and performs well without any issues.
from isbnlib import is_isbn10, is_isbn13
from typing import Union

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import Book




def validate_isbn(isbn: str) -> bool:
    return is_isbn10(isbn) or is_isbn13(isbn)


def fetch_book_from_api(isbn: str) -> Union[dict, None]:
    url = f"{settings.OPEN_LIBRARY_API_URL}/{isbn}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'records' in data and data['records']:
            return list(data['records'].values())[0]['data']
    except requests.RequestException as e:
        print(f"Error fetching book data: {e}")
    return None


def error_response(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def get_book_details_from_data(book_data: dict, isbn: str) -> dict:
    return {
        "isbn": isbn,
        "title": book_data.get("title", "Unknown Title"),
        "author": book_data.get("authors", [{}])[0].get("name", "Unknown Author"),
        "summary": book_data.get("notes", ""),
        "cover_url": book_data.get("cover", {}).get("medium", "")
    }


class FetchBookDetailsView(View):
    
    def get(self, request, isbn: str, *args, **kwargs) -> JsonResponse:
        if not validate_isbn(isbn):
            return error_response("Invalid ISBN")

        book_data = fetch_book_from_api(isbn)
        if not book_data:
            return error_response("Book not found", status=404)

        book_details = get_book_details_from_data(book_data, isbn)
        return JsonResponse(book_details)


@method_decorator(csrf_exempt, name='dispatch')
class BookView(View):

    def post(self, request, *args, **kwargs) -> JsonResponse:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response("Invalid JSON", status=400)

        isbn = body.get("isbn")
        if not isbn:
            return error_response("ISBN is required")

        if not validate_isbn(isbn):
            return error_response("Invalid ISBN")

        book_data = fetch_book_from_api(isbn)
        if not book_data:
            return error_response("Book not found", status=404)

        book_details = get_book_details_from_data(book_data, isbn)

        book, created = Book.objects.update_or_create(
            isbn=isbn,
            defaults={
                "title": book_details["title"],
                "author": book_details["author"],
                "summary": book_details["summary"],
                "cover_url": book_details["cover_url"]
            }
        )

        status_code = 201 if created else 200
        return JsonResponse(book_details, status=status_code)

    def get(self, request, *args, **kwargs) -> JsonResponse:
        books = list(Book.objects.values("isbn", "title", "author", "summary", "cover_url"))
        return JsonResponse(books, safe=False)