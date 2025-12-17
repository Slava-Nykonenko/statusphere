from rest_framework.pagination import PageNumberPagination


class ListsPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 100
