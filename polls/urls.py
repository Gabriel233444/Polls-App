from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
     # GET
    path('api/list/', views.PollsListViewSet.as_view(), name='list'),
     # POST
    path('api/add/', views.PollsCreatViewSet.as_view(), name='add'),
    path('api/choice/add/<int:pk>/', views.ChoiceAddViewSet.as_view(), name='add_choice'),
    #UPDATE
    path('api/edit/<int:pk>/', views.PollsEditViewSet.as_view(), name='edit'),
    path('api/edit/choice/<int:pk>/', views.ChoiceEditViewSet.as_view(), name='choice_edit'),
    # DELETE
    path('api/delete/<int:pk>/', views.PollsDeleteViewSet.as_view(), name='delete_poll'),
    path('end/<int:pk>/', views.endpoll, name='end_poll'),
    path('delete/choice/<int:pk>/', views.choice_delete, name='choice_delete'),
    
    path('<int:pk>/', views.poll_detail, name='detail'),
    path('<int:pk>/vote/', views.poll_vote, name='vote'),
]
