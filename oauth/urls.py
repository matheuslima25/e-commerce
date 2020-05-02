from django.urls import path

from oauth import views

urlpatterns = [
    # Signup
    path('signup/', views.CreateUserAndObtainJSONWebToken.as_view()),

    # Signin
    path('login/', views.ObtainJSONWebToken.as_view()),
    path('login/password-reset-key-request/', views.PasswordResetKeyWebToken.as_view()),
    path('login/password-reset-request/', views.PasswordResetWebToken.as_view()),
]
