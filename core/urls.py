from django.urls import include, path

from core import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('produtos/<slug:slug>/<int:pk>', views.ProductDetail.as_view(), name='product_detail'),
    path('produtos/<slug:slug>/', views.ProductCategoryView.as_view(), name='product_category'),
    path('load-products/', views.load_products, name='load-products'),

    path('login/', views.LoginAuthView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('forgot-password/', views.ForgetView.as_view(), name='forgot-password'),
    path('reset-password/', views.PasswordResetView.as_view(), name='reset-password'),
    path('reset-password-confirm/', views.PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]
