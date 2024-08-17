from django.urls import path

from user import views


urlpatterns = [
    path('login/', views.VerifyCodeAPIView.as_view()),
]