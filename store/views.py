from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from django.db.models import Q

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.

def store(request,category_slug=None):
    categories=None
    products=None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)#this will bring us categories
        products = Product.objects.filter(category=categories, is_available=True)#this will bring us products of above categories
        paginator = Paginator(products, 1)  #total no of products to display in one page
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)#6 products will be saved here
        product_count = products.count()
    else:

        products=Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)  #total no of products to display in one page
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)#3 products will be saved here
        product_count=products.count()
    context={
        'products':paged_products,
        'product_count':product_count,    
    }
    return render(request,'store/store.html',context)


def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart= CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    
    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)


    context={
       'single_product':single_product, 
       'in_cart':in_cart,
       'orderproduct':orderproduct,
       'reviews':reviews,
    } 
    return render(request,'store/product_detail.html',context)


def search(request):
    if 'keyword' in request.GET: #if get request has the keyword or not if it is true
        keyword = request.GET['keyword'] #storing thst in the keyword variable
        if keyword: #if keyword is not blank
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)) 
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request,'store/store.html',context)



def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') #to store the previous url
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews) #here instance is used bcoz to update review
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR') #this REMOTE_ADDR will store ip address
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
