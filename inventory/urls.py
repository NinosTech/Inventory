from django.contrib import admin
from django.urls import path
from .views import (
    Index, SignUpView, Dashboard, AddItem, EditItem, DeleteItem, 
    ProjectCreateView, ProjectInventoryView, UpdateQuantityView,
    AddItemToProject, DeleteProject, SearchResultsView
)
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('add-item/', AddItem.as_view(), name='add-item'),
    path('edit-item/<int:pk>/', EditItem.as_view(), name='edit-item'),
    path('delete-item/<int:pk>/', DeleteItem.as_view(), name='delete-item'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='inventory/logout.html'), name='logout'),

    path('project/<int:project_id>/inventory/', ProjectInventoryView.as_view(), name='project_inventory'),  # Inventory page for each project
    path('project/create/', ProjectCreateView.as_view(), name='create_project_page'),


    path('project/<int:project_id>/add-item/', AddItemToProject.as_view(), name='add-item-to-project'),
    path('delete-project/<int:pk>/', DeleteProject.as_view(), name='delete_project'),

    path('search/', SearchResultsView.as_view(), name='search_results'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)