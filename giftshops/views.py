from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from giftshops.models.giftshops import AddCategory, Product, CartItem, Order, OrderItem
from giftshops.serializers import AddCategorySerializer, ProductSerializer
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages



@method_decorator(login_required, name='dispatch')
class GiftShopView(TemplateView):
    """Giftshop view for the app"""

    template_name = "giftshop.html"

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["user_role"] = getattr(self.request.user, 'user_type', None)
        context["categories"] = AddCategory.objects.all()[:6]
        context["all_categories"] = AddCategory.objects.all()
        context["featured_products"] = featured_products
        context["new_arrivals"] = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
        context["best_sellers"] = Product.objects.filter(is_active=True).order_by('-sales_count')[:6]

        # Add organizations that have created products for the search filter
        context["product_organizations"] = User.objects.filter(
            id__in=Product.objects.filter(is_active=True).values_list('created_by_id', flat=True).distinct()
        ).distinct()

        return context

@method_decorator(login_required, name='dispatch')
class ShopView(TemplateView):
    template_name = "shop.html"

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, 'user_type', None) not in ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # ✅ Separate queries
        products = Product.objects.filter(created_by=user, is_featured=False)
        featured_products = Product.objects.filter(created_by=user, is_featured=True)

        # ✅ Paginate normal products (12 per page)
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get("page")
        products_page = paginator.get_page(page_number)

        # ✅ Paginate featured products (6 per page for example)
        featured_paginator = Paginator(featured_products, 6)
        featured_page_number = self.request.GET.get("featured_page")
        featured_page = featured_paginator.get_page(featured_page_number)

        # Orders that include these products
        orders = (
            Order.objects.filter(items__product__in=products | featured_products)
            .prefetch_related("items__product", "customer")
            .distinct()
        )

        context.update({
            "user": user,
            "user_role": user.user_type,
            "products": products_page,  # ✅ paginated products
            "featured_products": featured_page,  # ✅ paginated featured products
            "orders": orders,
            "categories": AddCategory.objects.all()[:6],
            "all_categories": AddCategory.objects.all(),
        })
        return context



@method_decorator(login_required, name='dispatch')
class CategoryView(TemplateView):
    """Category view for the app"""

    template_name = "category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["categories"] = AddCategory.objects.all()
        return context

@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    categories = AddCategory.objects.all()
    serializer = AddCategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_6_categories(request):
    categories = AddCategory.objects.all()[:6]  # Get only the first 6
    serializer = AddCategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_by_category(request, category_id):
    """Get products by category ID."""
    try:
        category = AddCategory.objects.get(id=category_id)
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except AddCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)

@login_required
def create_product(request):
    user = request.user
    allowed_roles = ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]

    if getattr(user, 'user_type', None) not in allowed_roles:
        messages.error(request, "Only registered providers or organizations can add products.")
        return redirect('giftshop')  # fallback: your homepage

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        price = request.POST.get("price")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        is_featured = "is_featured" in request.POST
        stock_quantity = request.POST.get("stock_quantity", 0)

        category = get_object_or_404(AddCategory, id=category_id)

        product = Product.objects.create(
            category=category,
            created_by=user,
            name=name,
            price=price,
            description=description,
            image=image,
            is_featured=is_featured,
            stock_quantity=int(stock_quantity) if stock_quantity else 0,
            is_active=True  # ✅ ensure new products are active
        )

        messages.success(request, f"Product '{name}' created successfully!")

        # 🔑 redirect to the category's product list instead of product detail
        return redirect('giftshops:category_products', category_id=category.id)

    categories = AddCategory.objects.all()
    return render(request, "create_product.html", {"categories": categories})

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def create_product(request):
#     """Handle both displaying the create form and saving the product."""
#     user = request.user
#     allowed_roles = ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]

#     # Role check
#     if getattr(user, 'user_type', None) not in allowed_roles:
#         if request.accepted_renderer.format == 'html':
#             messages.error(request, "Only registered providers or organizations can add products.")
#             return redirect("home")
#         return Response(
#             {"error": "Only registered providers or organizations can add products."},
#             status=403
#         )

#     if request.method == "GET":
#         # Show form
#         categories = AddCategory.objects.all()
#         return render(request, "create_product.html", {"categories": categories})

#     if request.method == "POST":
#         if request.accepted_renderer.format == 'html':
#             # HTML form submission
#             name = request.POST.get("name")
#             category_id = request.POST.get("category")
#             price = request.POST.get("price")
#             description = request.POST.get("description")
#             image = request.FILES.get("image")
#             is_featured = "is_featured" in request.POST

#             category = get_object_or_404(AddCategory, id=category_id)
#             Product.objects.create(
#                 category=category,
#                 created_by=user,
#                 name=name,
#                 price=price,
#                 description=description,
#                 image=image,
#                 is_featured=is_featured
#             )
#             messages.success(request, f"Product '{name}' created successfully!")
#             return redirect("product_list")  # Adjust to your product listing route

#         else:
#             # API JSON submission
#             data = request.data.copy()
#             data['created_by'] = user.id
#             serializer = ProductSerializer(data=data)
#             if serializer.is_valid():
#                 product = serializer.save()
#                 return Response(ProductSerializer(product).data, status=201)
#             return Response(serializer.errors, status=400)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def search_products(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    organisation_id = request.GET.get('organisation')
    price_range = request.GET.get('price_range')
    sort_option = request.GET.get('sort')

    # Start with active products
    products = Product.objects.filter(is_active=True)

    # Apply text search filter
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Apply category filter
    if category_id:
        try:
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass  # Invalid category ID

    # Apply organization filter
    if organisation_id:
        try:
            products = products.filter(created_by_id=organisation_id)
        except (ValueError, TypeError):
            pass  # Invalid organization ID

    # Apply price range filter
    if price_range:
        try:
            if price_range == '1-10':
                products = products.filter(price__gte=1, price__lte=10)
            elif price_range == '10-25':
                products = products.filter(price__gte=10, price__lte=25)
            elif price_range == '25-50':
                products = products.filter(price__gte=25, price__lte=50)
            elif price_range == '50-100':
                products = products.filter(price__gte=50, price__lte=100)
            elif price_range == '100-200':
                products = products.filter(price__gte=100, price__lte=200)
            elif price_range == '200-500':
                products = products.filter(price__gte=200, price__lte=500)
            elif price_range == '500-1000':
                products = products.filter(price__gte=500, price__lte=1000)
            elif price_range == '1000-plus':
                products = products.filter(price__gte=1000)
        except (ValueError, TypeError):
            pass  # Invalid price range

    # Apply sorting
    if sort_option:
        if sort_option == 'price_low':
            products = products.order_by('price')
        elif sort_option == 'price_high':
            products = products.order_by('-price')
        elif sort_option == 'newest':
            products = products.order_by('-created_at')
        elif sort_option == 'oldest':
            products = products.order_by('created_at')
        elif sort_option == 'name_asc':
            products = products.order_by('name')
        elif sort_option == 'name_desc':
            products = products.order_by('-name')
        elif sort_option == 'featured':
            products = products.order_by('-is_featured', '-created_at')
    else:
        # Default sorting: featured first, then by newest
        products = products.order_by('-is_featured', '-created_at')

    # Get the category object if filtering by category
    category = None
    if category_id:
        try:
            from .models import Category
            category = Category.objects.get(id=category_id)
        except (Category.DoesNotExist, ValueError, TypeError):
            pass

    return render(request, 'products_list.html', {
        'products': products,
        'category': category,
        'query': query,
        'selected_category': category_id,
        'selected_organisation': organisation_id,
        'selected_price_range': price_range,
        'selected_sort': sort_option,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def product_autocomplete(request):
    query = request.GET.get('q', '')
    if query:
        matches = Product.objects.filter(name__icontains=query, is_active=True)[:10]
        results = [{'id': p.id, 'name': p.name} for p in matches]
    else:
        results = []
    return Response(results)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {
        'product': product,
        'user': request.user  # add this to ensure user is available in template
    })

def featured_products(request):
    products = Product.objects.filter(is_featured=True, is_active=True)
    return render(request, 'products_list.html', {
        'products': products,
        'category': None,  # no category here
        'query': None,
    })

@login_required
def create_product_page(request):
    allowed_roles = ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]
    if getattr(request.user, 'role', None) not in allowed_roles:
        return redirect('giftshop')  # or raise 403

    return render(request, 'create_product.html')

# @login_required
# def create_product_page(request):
#     """Show the HTML form for creating a product (restricted to providers/orgs)."""
#     user = request.user

#     has_permission = (
#         hasattr(user, 'organization_profile') or
#         hasattr(user, 'individual_provider_profile')
#     )

#     if not has_permission:
#         messages.error(request, "Only registered providers or organizations can add products.")
#         return redirect("home")  # Change 'home' to your homepage route

#     categories = AddCategory.objects.all()

#     return render(request, "create_product.html", {
#         "categories": categories
#     })
def category_products(request, category_id):
    category = get_object_or_404(AddCategory, id=category_id)

    # default: show all active products
    products = Product.objects.filter(category=category, is_active=True)

    # if logged in as provider/organization → restrict to their own products
    if request.user.is_authenticated:
        if request.user.user_type in ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]:
            products = products.filter(created_by=request.user)

    # search filter
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'products_list.html', {
        'category': category,
        'products': products,
        'query': query,
    })


@login_required
def delete_product(request, pk):
    user = request.user
    allowed_roles = ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]

    if getattr(user, 'user_type', None) not in allowed_roles:
        return HttpResponseForbidden("You do not have permission to delete this product.")

    product = get_object_or_404(Product, pk=pk)

    if product.created_by != user:
        return HttpResponseForbidden("You can only delete your own products.")

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('giftshops:giftshop')  # changed to redirect shortcut

    # Optional: render a confirmation page (if you want)
    return render(request, 'confirm_delete.html', {'product': product})

@login_required
def edit_product(request, pk):
    user = request.user
    allowed_roles = ["INDIVIDUAL_PROVIDER", "ORGANIZATION"]

    if getattr(user, 'user_type', None) not in allowed_roles:
        messages.error(request, "Only registered providers or organizations can edit products.")
        return redirect('giftshops:giftshop')

    product = get_object_or_404(Product, pk=pk)

    if product.created_by != user:
        return HttpResponseForbidden("You can only edit your own products.")

    if request.method == "POST":
        # get data from POST request
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        price = request.POST.get("price")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        is_featured = "is_featured" in request.POST
        stock_quantity = request.POST.get("stock_quantity")

        category = get_object_or_404(AddCategory, id=category_id)

        # update fields
        product.name = name
        product.category = category
        product.price = price
        product.description = description
        if image:
            product.image = image
        product.is_featured = is_featured
        if stock_quantity is not None:
            product.stock_quantity = int(stock_quantity)
        product.save()

        messages.success(request, f"Product '{name}' updated successfully!")
        return redirect('giftshops:product_detail', pk=product.pk)

    else:
        categories = AddCategory.objects.all()
        return render(request, "edit_product.html", {
            "product": product,
            "categories": categories,
        })

@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Invalid request method")

    product = get_object_or_404(Product, pk=product_id)

    # Check if product is in stock
    if product.stock_quantity <= 0:
        messages.error(request, f"'{product.name}' is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'giftshops:giftshop'))

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        # Check if adding one more would exceed available stock
        if cart_item.quantity >= product.stock_quantity:
            messages.error(request, f"Only {product.stock_quantity} units of '{product.name}' are available.")
            return redirect(request.META.get('HTTP_REFERER', 'giftshops:giftshop'))
        cart_item.quantity += 1
        cart_item.save()
    else:
        # For new cart items, set quantity to 1
        cart_item.quantity = 1
        cart_item.save()

    # Reduce stock quantity
    product.stock_quantity -= 1
    product.save()

    messages.success(request, f"Added '{product.name}' to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'giftshops:giftshop'))
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    if request.method == "POST":
        # Restore stock quantity when removing from cart
        product = cart_item.product
        product.stock_quantity += cart_item.quantity
        product.save()

        cart_item.delete()
        messages.success(request, "Item removed from cart.")
        return redirect('giftshops:view_cart')
    return render(request, 'confirm_remove.html', {'cart_item': cart_item})

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    if request.method == "POST":
        new_quantity = int(request.POST.get('quantity', 1))
        old_quantity = cart_item.quantity
        product = cart_item.product

        if new_quantity > 0:
            quantity_difference = new_quantity - old_quantity

            # Check if we have enough stock for the increase
            if quantity_difference > 0 and quantity_difference > product.stock_quantity:
                messages.error(request, f"Only {product.stock_quantity + old_quantity} units of '{product.name}' are available.")
                return redirect('giftshops:view_cart')

            # Update stock quantity
            product.stock_quantity -= quantity_difference
            product.save()

            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Updated quantity for '{cart_item.product.name}'.")
        else:
            # Remove item and restore stock
            product.stock_quantity += old_quantity
            product.save()

            cart_item.delete()
            messages.success(request, f"Removed '{cart_item.product.name}' from your cart.")
        return redirect('giftshops:view_cart')
    return render(request, 'update_cart_item.html', {'cart_item': cart_item})
