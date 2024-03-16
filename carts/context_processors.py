from .models import Cart,CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            #if user is logged in then gives the count of the product based on the paticular user
            if request.user.is_authenticated: 
               cart_items = CartItem.objects.all().filter(user=request.user)
            else:    
               cart_items = CartItem.objects.all().filter(cart=cart[:1]) #if there are some many cart ids though it gives one cart id
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)