from django.db import models
from django.conf import settings


class Brand(models.Model):
    """Brands selling products through the digital giftshops."""

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='owned_brands'
    )

    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    website = models.URLField(blank=True)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """Customer orders for products."""

    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)

    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)

    order_date = models.DateTimeField(auto_now_add=True)

    payment_status = models.CharField(max_length=20, default='PENDING')
    transaction_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.full_name}"

class Product(models.Model):
    """Products sold through the digital giftshops."""
    category = models.ForeignKey(
        'AddCategory',
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products_created',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/')
    requires_prescription = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sales_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_out_of_stock(self):
        """Check if product is out of stock."""
        return self.stock_quantity <= 0

    @property
    def is_almost_out_of_stock(self):
        """Check if product is almost out of stock (5 or fewer items)."""
        return 0 < self.stock_quantity <= 5

    @property
    def stock_status(self):
        """Get stock status as a string."""
        if self.is_out_of_stock:
            return "out_of_stock"
        elif self.is_almost_out_of_stock:
            return "almost_out_of_stock"
        else:
            return "in_stock"

class AddCategory(models.Model):
    """Model to add categories for products."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category_photo = models.ImageField(upload_to='categories_photo/', blank=False, null=True)

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    """Individual items within an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price

class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        # Use discount price if available, otherwise normal price
        price = self.product.discount_price if self.product.discount_price else self.product.price
        return price * self.quantity
