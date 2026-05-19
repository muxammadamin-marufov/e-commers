from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Cart, Order, OrderItem
from django.db.models import Q
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.http import JsonResponse
import json
import requests
from .config import TOKEN, CHAT_ID

User = get_user_model()

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
    return render(request, 'index.html', {'products': products, 'categories': categories, 'query': query, 'total': total})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        phone_number = request.POST.get("phone_number")
        fullname = request.POST.get("fullname")
        password1 = request.POST.get("password")
        password2 = request.POST.get("password2")
        is_seller_input = request.POST.get("is_seller") == "on"

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu foydalanuvchi nomi allaqachon mavjud")
            return redirect("register")

        if not phone_number.startswith("998") or len(phone_number) != 12:
            messages.error(request, "Format xato: 998XXXXXXXXX ko'rinishida bo'lsin")
            return redirect("register")

        if password1 != password2:
            messages.error(request, "Parollar bir xil emas")
            return redirect("register")
        
        user = User.objects.create_user(
            username=username, password=password1, first_name=fullname,
            phone_number=phone_number, is_seller=is_seller_input
        )
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

# --- SOTUVCHI DASHBOARD LOGIKASI ---
@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        messages.error(request, "Siz sotuvchi emassiz!")
        return redirect('index')
    
    my_products = Product.objects.filter(seller=request.user)
    categories = Category.objects.all()
    return render(request, 'dashboard.html', {'products': my_products, 'categories': categories})

@login_required
def add_product(request):
    if request.method == 'POST' and request.user.is_seller:
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=category_id)
        
        Product.objects.create(
            seller=request.user, name=name, price=price, stock=stock,
            category=category, description=description, image=image
        )
        messages.success(request, "Mahsulot muvaffaqiyatli qo'shildi!")
        return redirect('seller_dashboard')
    return redirect('index')

# --- GEMINI AI INTEGRATSIYASI (AJAX ORQALI) ---
@login_required
def generate_description(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('name')
            
            # Bu yerga o'zingizning haqiqiy OpenRouter yoki Gemini kalitingizni qoying
            api_key = "KAFEDRA_YOKI_OPENROUTER_KEY" 
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            prompt = f"Men e-commerce saytida '{product_name}' sotmoqchiman. Iltimos, ushbu mahsulot uchun xaridorlarni jalb qiladigan, juda chiroyli, xususiyatlari yozilgan, o'zbek tilida professional marketing tavsifi (description) yozib ber. Matn juda uzun bo'lmasin, silliq va tushunarli bo'lsin."
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "google/gemini-2.5-flash", # yoki o'zingiz ishlatayotgan model nomi
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            ai_text = response_data['choices'][0]['message']['content']
            return JsonResponse({'success': True, 'description': ai_text})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

# --- QOLGAN FUNKSIYALAR (SAVATCHA VA BUYURTMA) ---
def product_about(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'product_about.html', {'product': product, 'related_products': related_products})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock > 0:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
        messages.success(request, f"{product.name} savatga qo'shildi")
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
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        
        if action == 'delete':
            cart_item.delete()
            return JsonResponse({'success': True, 'deleted': True, 'cart_total': float(get_total(request))})
        
        if action == 'plus' and cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        elif action == 'minus' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        
        cart_item.save()
        return JsonResponse({
            'success': True, 'deleted': False, 'item_qty': cart_item.quantity,
            'item_total': float(cart_item.product.price * cart_item.quantity),
            'cart_total': float(get_total(request))
        })

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists(): return redirect('index')
    total = get_total(request)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        order = Order.objects.create(user=request.user, full_name=full_name, phone=phone, address=address, total_amount=total)
        items_summary = ""
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
            items_summary += f"- {item.product.name} x {item.quantity}\n"
            item.product.stock -= item.quantity
            item.product.save()

        message_text = f"🛍 <b>Yangi buyurtma!</b>\n━━━━━━━━━━━━━━━\n👤 <b>Mijoz:</b> {full_name}\n📞 <b>Tel:</b> {phone}\n📍 <b>Manzil:</b> {address}\n💰 <b>Jami:</b> {total:,} so'm\n━━━━━━━━━━━━━━━\n🛒 <b>Tarkibi:</b>\n{items_summary}"
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": message_text, "parse_mode": "HTML"})
        except: pass
        
        cart_items.delete()
        return redirect('order-success')
    return render(request, 'checkout.html', {'total': total})

def success_view(request):
    return render(request, 'success.html')