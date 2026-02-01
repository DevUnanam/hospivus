from django.urls import path
from giftshops import views

app_name = "giftshops"

urlpatterns = [
    path('giftshop/', views.GiftShopView.as_view(), name='giftshop'),
    path('shop/manage/', views.ShopView.as_view(), name='manage_shop'),
    path('categories/', views.get_categories, name='getcategories'),
    path('categories/6/', views.get_6_categories, name='get6categories'),
    path('giftshop/categories/', views.CategoryView.as_view(), name='giftshop_categories'),
    path('categories/<int:category_id>/products/', views.get_products_by_category, name='get_products_by_category'),
    # path('products/create/', views.create_product, name='create_product'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('shop/category/<int:category_id>/', views.category_products, name='shop_category_products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('giftshop/search/', views.search_products, name='search_products'),
    path('api/product-autocomplete/', views.product_autocomplete, name='product_autocomplete'),
    path('featured/', views.featured_products, name='featured_products'),
    path('products/create/', views.create_product, name='create_product'),  # API
    # path('products/create/page/', views.create_product_page, name='create_product_page'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

]