from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_seller = models.BooleanField(default=False, verbose_name="Sotuvchimisiz?")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqam")

    def __str__(self):
        return f"{self.username} ({'Sotuvchi' if self.is_seller else 'Xaridor'})"

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, null=True, blank=True)
    icon = models.CharField(max_length=50, default="bi-grid", help_text="Bootstrap Icons nomini yozing (masalan: bi-laptop)")

    class Meta:
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name

class Product(models.Model):
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products', limit_choices_to={'is_seller': True})
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Kategoriyasi")
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    description = models.TextField(verbose_name="Batafsil tavsifi")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi (so'm)")
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Chegirmadagi narxi (ixtiyoriy)")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Mahsulot rasmi")
    stock = models.PositiveIntegerField(default=10, verbose_name="Ombordagi soni")
    is_active = models.BooleanField(default=True, verbose_name="Sotuvda bormi?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def get_current_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.get_current_price

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda ⏳'),
        ('processing', 'Tayyorlanmoqda 📦'),
        ('shipped', 'Yo\'lda 🚚'),
        ('delivered', 'Yetkazib berildi ✅'),
        ('canceled', 'Bekor qilindi ❌'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=255, verbose_name="Ism va Familiya")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    address = models.TextField(verbose_name="Yetkazish manzili")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Jami summa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Buyurtma holati")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Buyurtma #{self.id} — {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'O\'chirilgan mahsulot'}"