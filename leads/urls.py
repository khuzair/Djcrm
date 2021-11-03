from django.urls import path
from .views import (
    lead_list, lead_detail, lead_create, lead_update, lead_delete, 
    LeadListView,
    LeadDetailView,
    LeadCreateView,
    LeadUpdateView,
    LeadDeleteView,
    AssignAgentView,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    LeadCategoryUpdateView
    )

app_name = "leads"

urlpatterns = [
    path('', LeadListView.as_view() , name='lead-list'),
    path('<int:pk>/', LeadDetailView.as_view() , name='lead-detail'),
    path('create/', LeadCreateView.as_view() , name='lead-create'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='lead-delete'),
    path('<int:pk>/assign_agent/', AssignAgentView.as_view(), name='assign-agent'),
    path('categories_update/<int:pk>/',LeadCategoryUpdateView.as_view(), name="lead-category-update"),
    path('categories/',CategoryListView.as_view(), name="category-list"),
    path('categories_detail/<int:pk>/',CategoryDetailView.as_view(), name="category-detail"),
    path('create_category/',CategoryCreateView.as_view(), name="create-category"),
    path('<int:pk>/category_update/',CategoryUpdateView.as_view(), name="category-update"),
    path('<int:pk>/category_delete/',CategoryDeleteView.as_view(), name="category-delete")
]
    