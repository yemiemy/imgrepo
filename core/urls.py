from django.urls import path
from .views import (
    HomeView,  
    ItemDetailView,
    add_to_cart, 
    remove_from_cart,
    OrderSummaryView,
    remove_single_item_from_cart,
    increment_order_item_qty,
    PaymentView,
    search,

    TagItemListView,
    AuthorItemListView,
    ItemCreateView,
    ItemUpdateView,
    ItemDeleteView,
    thanks
    )

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('checkout/payment/order/successful/', thanks, name="thanks"),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('photo/<slug>/', ItemDetailView.as_view(), name="item-detail"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name="remove-from-cart"),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('increase-photo-qty-in-cart/<slug>/', increment_order_item_qty, name="increase_item_qty"),
    path('checkout/payment/', PaymentView.as_view(), name="payment"),
    path('category/<str:name>', TagItemListView.as_view(), name='item_tag'),
    path('photo/<int:id>/<str:first_name>/', AuthorItemListView.as_view(), name='user_item'),

    path('search/', search, name='search'),
    
    path('upload/new/photo/', ItemCreateView.as_view(), name='item_create'),
    path('photo/<int:pk>-<str:slug>/update/', ItemUpdateView.as_view(), name='item_update'),
    path('photo/<int:pk>-<str:slug>/delete/', ItemDeleteView.as_view(), name='item_delete')
]
