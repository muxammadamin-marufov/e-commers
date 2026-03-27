from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Cart, Order
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import requests
from .config import TOKEN, CHAT_ID
def get_total(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        return sum(item.product.price * item.quantity for item in cart_items)
    return 0
def index(request):
    if not request.user.is_authenticated:
        return redirect("login")
    query = request.GET.get('q')
    start = request.GET.get('start')
    finish = request.GET.get('finish')
    categories = Category.objects.all()
    products = Product.objects.all()

    if start and finish:
        products = products.filter(price__range=[start, finish])

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query)
        )
    
    total = get_total(request)
    
    return render(request, 'index.html', {
        'products': products, 
        'categories': categories,
        'query': query,
        'total': total
    })
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        fullname = request.POST.get("fullname")
        password1 = request.POST.get("password")
        password2 = request.POST.get("password2")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu foydalanuvchi nomi allaqachon mavjud")
            return redirect("register")

        if not phone_number.startswith("998") or len(phone_number) != 12:
            messages.error(request, "Format xato: 998XXXXXXXXX ko'rinishida bo'lsin")
            return redirect("register")

        if password1 != password2:
            messages.error(request, "Parollar bir xil emas")
            return redirect("register")
        
        if len(password1) < 8:
            messages.warning(request, "Parol kamida 8 ta belgidan iborat bo'lishi kerak")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password1, first_name=fullname)
        user.save()
        
        messages.success(request, "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!")
        return redirect("login")
        
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        user_input = request.POST.get("user")
        password = request.POST.get("password")
        user = authenticate(request, username=user_input, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Login yoki parol xato")
    return render(request, "login.html")

def product_about(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'product_about.html', {
        'product': product,
        'related_products': related_products
    })
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock > 0:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, "Omborda boshqa mahsulot qolmadi")
        messages.success(request, f"{product.name} savatga qo'shildi")
    else:
        messages.error(request, "Mahsulot tugagan")
    return redirect('index')

@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = get_total(request)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        try:
            new_qty = int(data.get('quantity', 0))
        except (ValueError, TypeError):
            new_qty = 1
        
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        stock = cart_item.product.stock
        message = ""
        error = False

        if action == 'delete' or (action == 'manual' and new_qty <= 0):
            cart_item.delete()
            return JsonResponse({'success': True, 'deleted': True, 'cart_total': float(get_total(request))})

        if action == 'manual' or action == 'plus':
            requested_qty = new_qty if action == 'manual' else cart_item.quantity + 1
            if requested_qty > stock:
                cart_item.quantity = stock
                message = f"Omborda bor-yog'i {stock} ta mahsulot bor!"
                error = True
            else:
                cart_item.quantity = requested_qty
        
        elif action == 'minus':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return JsonResponse({'success': True, 'deleted': True, 'cart_total': float(get_total(request))})

        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'deleted': False,
            'item_qty': cart_item.quantity,
            'item_total': float(cart_item.product.price * cart_item.quantity),
            'cart_total': float(get_total(request)),
            'message': message,
            'error': error
        })

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Savatingiz bo'sh!")
        return redirect('index')
    
    total = get_total(request)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        items_summary = "\n".join([f"• {item.product.name} ({item.quantity} dona) - {item.product.price * item.quantity:,} so'm" for item in cart_items])
        Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            total_amount=total,
        )
        message_text = (
            f"🛍 <b>Yangi buyurtma!</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 <b>Mijoz:</b> {full_name}\n"
            f"📞 <b>Tel:</b> {phone}\n"
            f"📍 <b>Manzil:</b> {address}\n"
            f"💰 <b>Jami:</b> {total:,} so'm\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🛒 <b>Mahsulotlar:</b>\n{items_summary}"
        )

        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": message_text, "parse_mode": "HTML"})
        except Exception as e:
            print(f"Telegram error: {e}")
        for item in cart_items:
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        cart_items.delete()
        messages.success(request, "Buyurtmangiz muvaffaqiyatli qabul qilindi!")
        return redirect('order_success')

    return render(request, 'checkout.html', {'total': total})

def success_view(request):
    return render(request, 'success.html')