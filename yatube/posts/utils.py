from yatube.settings import NUMBER_OF_POSTS
from django.core.paginator import Paginator


def pagination(queryset, request):
    paginator = Paginator(queryset, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
