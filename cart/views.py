from django.shortcuts import redirect, render,get_object_or_404
from products.models import Product
from .cart_logic import Cart
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CartItem
from django.views.decorators.http import require_POST

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Increased quantity in cart.')
        else:
            messages.warning(request, 'No more stock available.')
    else:
        if product.stock > 0:
            messages.success(request, 'Added to cart.')
        else:
            messages.warning(request, 'This product is out of stock.')
            return redirect('product_list')

    return redirect('product_list')



@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.name} removed from cart.")
    return redirect('cart:view_cart')


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)  # ✅ use the @property directly
    return render(request, 'cart/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@require_POST
@login_required
def update_quantity(request, product_id):
    action = request.POST.get('action')
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    product = cart_item.product

    if action == 'increase':
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
        else:
            messages.warning(request, 'No more stock available.')
            return redirect('cart:view_cart')

    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
            return redirect('cart:view_cart')

    cart_item.save()
    return redirect('cart:view_cart')


