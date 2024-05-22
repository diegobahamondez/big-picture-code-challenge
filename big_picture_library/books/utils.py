import requests

# there are several methods for validating ISBN, including creating your own algorithms.
# But i think the less code you have to mantain, the better for the project.
# I also checked the github of this library (isbnlib) and performs well without any issues.
from isbnlib import is_isbn10, is_isbn13

from typing import Union

from bs4 import BeautifulSoup

from django.conf import settings
from django.http import JsonResponse


def error_response(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


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


def get_summary(book_data: dict):
    summary = book_data["details"].get("details", {}).get("description", None)
    if isinstance(
        summary, dict
    ):  # from the records i've seen, the summary can come in the form of dict with "value" and "name" keys, or as a string directly
        summary = summary.get(
            "value", None
        )  # in some cases, it appears a description on the page, but the api doesn't return it. eg: 1526617161
    if summary is not None:
        return summary
    # so when the summary is not in the api response, time to do some web scrapping
    url = book_data.get("recordURL", None)
    if url is not None:
        summary = extract_book_description_from_url(url)
        return summary
    return "failed to fetch summary"


def extract_book_description_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        # parse HTML
        soup = BeautifulSoup(response.content, "html.parser")
        # find the div
        description_element = soup.find("div", class_="book-description")

        if description_element:
            # extract description
            description = description_element.find("p").get_text(strip=True)
            return description
        return "Description not found."
    return "Failed to fetch summary"


def get_authors(book_data: dict):
    authors_records = book_data["data"].get(
        "authors", [{}]
    )  # in case there's more than one author,
    authors_list = [i["name"] for i in authors_records]  # we make a list of them
    authors_string = ", ".join(
        authors_list
    )  # and then join them as author1, author2 etc
    return authors_string


def get_book_details_from_data(book_data: dict, isbn: str) -> dict:
    return {
        "isbn": isbn,
        "title": book_data["data"].get("title", "Unknown Title"),
        "author": get_authors(book_data),
        "summary": get_summary(book_data),
        "cover_url": book_data["data"].get("cover", {}).get("medium", ""),
    }
