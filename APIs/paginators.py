from rest_framework.pagination import PageNumberPagination 
from rest_framework.response import Response

#Defining a custom paginator
class CustomPaginator(PageNumberPagination):
    page_size = 10 
    max_page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'size' 

    def get_paginated_response(self, data):
        return Response({
                'total_items': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'results': data
            })
