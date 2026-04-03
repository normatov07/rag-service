from rest_framework.pagination import PageNumberPagination as DefaultPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DefaultPageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_page_size(self, request):
        try:
            page_size = int(request.query_params.get(self.page_size_query_param, self.page_size))
            return min(page_size, self.max_page_size)
        except (TypeError, ValueError):
            return self.page_size

    def get_paginated_response(self, data):
        return Response({
            "total": self.page.paginator.count,
            "current_page": self.page.number,
            "last_page": self.page.paginator.num_pages,
            "per_page": self.get_page_size(self.request),
            "next": self.page.next_page_number() if self.page.has_next() else None,
            "previous": self.page.previous_page_number() if self.page.has_previous() else None,
            "results": data
        })
