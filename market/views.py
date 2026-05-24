from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.http import JsonResponse
import json
import requests
from .models import Product, Category, Cart, Order, OrderItem
from .config import TOKEN, CHAT_ID
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required

# PEXELS API orqali rasmsiz mahsulotlarga avtomatik rasm topish
@staff_member_required # Faqat adminlar ishlata oladi
def auto_fill_empty_images(request):
    # Rasmi yo'q (bo'sh) mahsulotlarni topamiz
    empty_products = Product.objects.filter(image__exact='') | Product.objects.filter(image__isnull=True)
    
    if not empty_products.exists():
        messages.success(request, "Ombordagi barcha mahsulotlarning rasmi bor! Yangilashga hojat yo'q.")
        return redirect('index')

    # DIQQAT: O'zingizning tekin Pexels API kalitingizni shu yerga qo'yasiz
    PEXELS_API_KEY = "MwOE4vTUFu9MWjXGBbwsuueU8xk4Ink8RsPSyaaY3CUV8rU7h0t8JxdI"
    headers = {"Authorization": PEXELS_API_KEY}
    
    updated_count = 0

    for product in empty_products:
        # Mahsulot nomi bo'yicha rasm qidiramiz (Masalan: "Noutbuk", "Smartfon")
        search_query = product.name
        url = f"https://api.pexels.com/v1/search?query={search_query}&per_page=1"
        
        try:
            response = requests.get(url, headers=headers).json()
            
            # Agar rasm topilsa
            if response.get('photos') and len(response['photos']) > 0:
                # Eng sifatli rasm linkini olamiz
                img_url = response['photos'][0]['src']['large']
                
                # Rasmni yuklab olamiz
                img_response = requests.get(img_url)
                
                if img_response.status_code == 200:
                    # Fayl nomi yaratamiz (bo'sh joylarni chiziqchaga almashtiramiz)
                    file_name = f"{product.name.replace(' ', '_')}.jpg"
                    
                    # Django modeliga rasmni saqlaymiz
                    product.image.save(file_name, ContentFile(img_response.content), save=True)
                    updated_count += 1
        except Exception as e:
            print(f"Xatolik yuz berdi ({product.name}): {e}")
            continue

    messages.success(request, f"Ajoyib! Jami {updated_count} ta mahsulotga avtomatik rasm topildi va joylandi.")
    return redirect('index')
User = get_user_model()

def get_cart_data(request):
    """Foydalanuvchi savatchasidagi jami summa va mahsulotlar sonini qaytaruvchi yordamchi funksiya"""
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_sum = sum(item.total_price() for item in cart_items)
        total_count = sum(item.quantity for item in cart_items)
        return total_sum, total_count
    return 0, 0
@login_required(login_url='login')
def index(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', None)
    start_price = request.GET.get('start')
    finish_price = request.GET.get('finish')

    categories = Category.objects.all()
    products = Product.objects.all().order_by('-id')[:50]

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if start_price and finish_price:
        products = products.filter(price__range=[start_price, finish_price])
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    cart_total, cart_count = get_cart_data(request)
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'current_category': category_slug
    }
    return render(request, 'index.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
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
            messages.error(request, "Telefon format xato: 998XXXXXXXXX ko'rinishida bo'lsin")
            return redirect("register")

        if password1 != password2:
            messages.error(request, "Kiritilgan parollar mos kelmadi")
            return redirect("register")
        
        user = User.objects.create_user(
            username=username, password=password1, first_name=fullname,
            phone_number=phone_number, is_seller=is_seller_input
        )
        messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz! Tizimga kiring.")
        return redirect("login")
        
    return render(request, "register.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == "POST":
        user_input = request.POST.get("user")
        password = request.POST.get("password")
        user = authenticate(request, username=user_input, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Login yoki parol noto'g'ri")
    return render(request, "login.html")

@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        messages.error(request, "Ushbu sahifa faqat sotuvchilar uchun!")
        return redirect('index')
    
    my_products = Product.objects.filter(seller=request.user)
    categories = Category.objects.all()
    cart_total, cart_count = get_cart_data(request)
    
    return render(request, 'dashboard.html', {
        'products': my_products, 
        'categories': categories,
        'cart_total': cart_total,
        'cart_count': cart_count
    })
@login_required
def edit_product_view(request, product_id):
    # Agar mahsulot boshqa seller'niki bo'lsa, sahifa 404 (Topilmadi) xatosini beradi
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description', '')
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
            
        product.save()
        messages.success(request, f'"{product.name}" muvaffaqiyatli yangilandi!')
        return redirect('seller_dashboard')
        
    return render(request, 'edit_product.html', {'product': product})

# 3. O'chirish: Faqat o'zining mahsulotini o'chirish (Xavfsiz)
@login_required
def delete_product_view(request, product_id):
    if request.method == 'POST':
        # Xavfsizlik uchun seller=request.user sharti bu yerda ham shart
        product = get_object_or_404(Product, id=product_id, seller=request.user)
        product_name = product.name
        product.delete()
        messages.success(request, f'"{product_name}" ombordan butunlay o‘chirildi!')
    return redirect('dashboard')
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
        messages.success(request, "Mahsulot muvaffaqiyatli sotuvga qo'shildi!")
        return redirect('seller_dashboard')
    return redirect('index')
@login_required(login_url='login')
def product_about(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    cart_total, cart_count = get_cart_data(request)
    
    return render(request, 'product_about.html', {
        'product': product, 
        'related_products': related_products,
        'cart_total': cart_total,
        'cart_count': cart_count
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
                messages.success(request, f"{product.name} miqdori oshirildi.")
            else:
                messages.warning(request, "Omborda bu mahsulotdan boshqa qolmagan.")
        else:
            messages.success(request, f"{product.name} savatga qo'shildi.")
    else:
        messages.error(request, "Mahsulot zaxirada tugagan.")
    return redirect('index')
@login_required(login_url='login')
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total, count = get_cart_data(request)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total, 'cart_count': count})

@csrf_exempt
@login_required
def update_cart_view(request, product_id):  # Funksiya nomi sizda boshqacha bo'lishi mumkin
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            # JS dan kelgan miqdorni butun son tipiga o'tkazamiz
            quantity = int(data.get('quantity', 1)) 
            
            # Savatni sessiyadan olamiz (agar bo'lmasa bo'sh lug'at)
            cart = request.session.get('cart', {})
            product_id_str = str(product_id)
            
            product = get_object_or_404(Product, id=product_id)
            
            # Agar mahsulot savatda hali yo'q bo'lsa, struktura yaratamiz
            if product_id_str not in cart:
                cart[product_id_str] = {'quantity': 0, 'price': float(product.price)}
            
            #--- AMALLARNI TEKSHIRISH ---
            if action == 'plus':
                if cart[product_id_str]['quantity'] < product.stock:
                    cart[product_id_str]['quantity'] += 1
                    
            elif action == 'minus':
                cart[product_id_str]['quantity'] -= 1
                if cart[product_id_str]['quantity'] <= 0:
                    del cart[product_id_str]
                    
            elif action == 'manual':
                # MANA SHU JOYI ENG MUHIMI! 
                # Miqdorni qo'shmaymiz, to'g'ridan-to'g'ri foydalanuvchi yozgan songa tenglaymiz
                if quantity <= 0:
                    if product_id_str in cart: del cart[product_id_str]
                elif quantity <= product.stock:
                    cart[product_id_str]['quantity'] = quantity
                else:
                    cart[product_id_str]['quantity'] = product.stock # Ombordagidan ko'p yozsa, borini beradi
                    
            elif action == 'delete':
                if product_id_str in cart:
                    del cart[product_id_str]
            
            # Django sessiyasini majburiy yangilaymiz (Aks holda xotirada qolmaydi)
            request.session['cart'] = cart
            request.session.modified = True
            
            # Qaytarish uchun ma'lumotlarni hisoblaymiz
            item_qty = cart.get(product_id_str, {}).get('quantity', 0)
            item_total = item_qty * float(product.price)
            
            # Savatdagi barcha narsalarning umumiy summasi
            cart_total = sum(item['quantity'] * float(item['price']) for item in cart.values())
            
            return JsonResponse({
                'success': True,
                'deleted': action == 'delete' or item_qty <= 0,
                'item_qty': item_qty,
                'item_total': item_total,
                'cart_total': cart_total
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'message': 'Noto‘g‘ri so‘rov'}, status=400)
@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists(): 
        return redirect('index')
        
    total, count = get_cart_data(request)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        order = Order.objects.create(user=request.user, full_name=full_name, phone=phone, address=address, total_amount=total)
        items_summary = ""
        
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, price=item.product.get_current_price, quantity=item.quantity)
            items_summary += f"📦 {item.product.name} — {item.quantity} ta x {item.product.get_current_price:,} so'm\n"
            
            # Ombordan ayirish
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save()

        # Telegram professional chek tizimi
        message_text = (
            f"🛍 <b>YANGI BUYURTMA</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Buyurtma raqami:</b> #{order.id}\n"
            f"👤 <b>Mijoz:</b> {full_name}\n"
            f"📞 <b>Tel:</b> {phone}\n"
            f"📍 <b>Manzil:</b> {address}\n"
            f"💰 <b>Jami summa:</b> {total:,} so'm\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🛒 <b>Xaridlar tarkibi:</b>\n{items_summary}"
        )
        
        if TOKEN and CHAT_ID:
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": CHAT_ID, "text": message_text, "parse_mode": "HTML"}, timeout=5)
            except Exception:
                pass
        
        cart_items.delete()
        return redirect('order-success')
        
    return render(request, 'checkout.html', {'total': total, 'cart_count': count})

def success_view(request):
    return render(request, 'success.html')

def live_search(request):
    query = request.GET.get('q', '')
    results = []
    
    if len(query) > 1: # Kamida 2 ta harf yozilganda qidiradi
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        )[:6] # Maksimal 6 ta taklif ko'rsatiladi (Uzum kabi ixcham bo'lishi uchun)
        
        for p in products:
            results.append({
                'id': p.id,
                'name': p.name,
                'category': p.category.name,
                'price': f"{int(p.price):,}".replace(",", " ") + " so'm"
            })
            
    return JsonResponse({'results': results})
@login_required
def create_product_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description', '')
        image = request.FILES.get('image') # Rasm yuklansa oladi, bo'lmasa bo'sh qoladi
        
        # Mahsulotni yaratamiz, lekin srazu bazaga saqlamay turamiz
        product = Product(
            name=name,
            price=price,
            stock=stock,
            description=description,
            image=image,
            seller=request.user # ENG MUHIMI: Sotuvchini avtomatik o'zi aniqlaydi!
        )
        product.save()
        
        messages.success(request, f'"{name}" muvaffaqiyatli omborga qo‘shildi!')
        return redirect('dashboard')
        
    return render(request, 'create_product.html')