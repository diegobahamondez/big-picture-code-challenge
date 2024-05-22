import requests

# there are several methods for validating ISBN, including creating your own algorithms. But from what
# I've learned I can say: The less code you have to mantain, the better for the project.
# I also checked the github of this library and performs well without any issues.
from isbnlib import is_isbn10, is_isbn13
from typing import Union

from django.conf import settings
from django.http import JsonResponse


def validate_isbn(isbn: str) -> bool:
    return is_isbn10(isbn) or is_isbn13(isbn)


def fetch_book_from_api(isbn: str) -> Union[dict, None]:
    url = f"{settings.OPEN_LIBRARY_API_URL}/{isbn}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "records" in data and data["records"]:
            return list(data["records"].values())[0]
    except requests.RequestException as e:
        print(f"Error fetching book data: {e}")
    return None


def error_response(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)

def get_summary(book_data: dict):
    summary = book_data["details"].get("details", {}).get("description", "no description")
    if isinstance(summary, dict):
        summary = summary.get("value", "no description")
    return summary

def get_book_details_from_data(book_data: dict, isbn: str) -> dict:
    return {
        "isbn": isbn,
        "title": book_data["data"].get("title", "Unknown Title"),
        "author": book_data["data"].get("authors", [{}])[0].get("name", "Unknown Author"),
        "summary": get_summary(book_data),
        "cover_url": book_data["data"].get("cover", {}).get("medium", ""),
        }
