from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "crudkit"

urlpatterns = [
    path('<str:app_label>/<str:model_name>/', views.read_items, name='crud-list'),
    path('<str:app_label>/<str:model_name>/<int:pk>/', views.item, name='crud-detail'),
    path('<str:app_label>/<str:model_name>/create/', views.create_item, name='crud-create'),
    path('<str:app_label>/<str:model_name>/<int:id>/update/', views.update_item, name='crud-update'),
    path('<str:app_label>/<str:model_name>/<int:id>/delete/', views.delete_item, name='crud-delete'),
    path('<tsr:app_label>/<str:model_name>/create_category/', views.create_category, name='create_category'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


