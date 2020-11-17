from django.urls import path
from .views import CallbackView

urlpatterns = [
    path('callback/', CallbackView.as_view(), name='callback'),
]
