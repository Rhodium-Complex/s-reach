#from library.views import home
from django.urls import path
from .views import sellerOrderClass, searchClass , resultClass, createClass, updateClass, orderClass,sellerOrderedClass
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('search/', searchClass.as_view()),
    path('result/', resultClass.as_view()),
    path('update/<int:pk>', updateClass.as_view()),
    path('create/', createClass.as_view()),
    path('seller-order/', sellerOrderClass.as_view()),
    path('seller-ordered/', sellerOrderedClass.as_view()),
    path('order/<int:pk>', orderClass.as_view()),
    path('', searchClass.as_view()),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)