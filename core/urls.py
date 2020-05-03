from django.urls import include, path

from core import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('<slug:slug>/<int:pk>', views.ProductDetail.as_view(), name='product_detail'),
    path('<slug:slug>/', views.ProductCategoryView.as_view(), name='product_category'),
]
