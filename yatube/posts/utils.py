from django.core.paginator import Paginator

from yatube.settings import NUMBER_OF_POSTS


def pagination(queryset, request):
    paginator = Paginator(queryset, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
