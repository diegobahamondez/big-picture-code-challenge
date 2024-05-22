import json


from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Book
from .utils import (
    validate_isbn,
    fetch_book_from_api,
    error_response,
    get_book_details_from_data,
)


class FetchBookDetailsView(View):

    def get(self, request, isbn: str, *args, **kwargs) -> JsonResponse:
        if not validate_isbn(isbn):
            return error_response("Invalid ISBN")

        book_data = fetch_book_from_api(isbn)
        if not book_data:
            return error_response("Book not found", status=404)

        book_details = get_book_details_from_data(book_data, isbn)
        return JsonResponse(book_details)


@method_decorator(csrf_exempt, name="dispatch")
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
                "cover_url": book_details["cover_url"],
            },
        )

        status_code = 201 if created else 200
        return JsonResponse(book_details, status=status_code)

    def get(self, request, *args, **kwargs) -> JsonResponse:
        books = list(
            Book.objects.values("isbn", "title", "author", "summary", "cover_url")
        )
        return JsonResponse(books, safe=False)
