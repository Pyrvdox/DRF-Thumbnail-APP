from django.urls import path
from .views import LoginView, logoutView, ListView, AddView, DetailView, ThumbnailView, ExpiringLinkCreateView, ViewImageView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logoutView, name='logout'),
    path('list/', ListView.as_view(), name='list'),
    path('add/', AddView.as_view(), name='add'),
    path('details/<int:pk>/', DetailView.as_view(), name='details'),
    path('thumbnail/<str:height>/<str:image_id>', ThumbnailView.as_view(), name='thumbnail'),
    path('imagelink/', ExpiringLinkCreateView.as_view(), name='imagelink'),
    path('view-image/<str:unique_key>/', ViewImageView.as_view(), name='view-image'),
]
