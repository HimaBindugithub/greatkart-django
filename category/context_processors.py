from .models import Category


def menu_links(request):
    links=Category.objects.all() #to fetch all categories
    return dict(links=links)#it brings all category lists it will stores them into the above links