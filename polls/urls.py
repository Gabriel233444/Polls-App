from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
     # GET
    path('api/poll/list/', views.PollsListViewSet.as_view(), name='poll_list'),
     # POST
    path('api/poll/add/', views.PollsCreatViewSet.as_view(), name='poll_add'),
    path('api/choice/add/', views.ChoiceAddViewSet.as_view(), name='choice_add'),
    path('api/vote/add/', views.VoteAddViewSet.as_view(), name='vote_add'),
    # UPDATE
    path('api/edit/poll/<int:pk>/', views.PollsEditViewSet.as_view(), name='poll_edit'),
    path('api/edit/choice/<int:pk>/', views.ChoiceEditViewSet.as_view(), name='choice_edit'),
    path('api/edit/vote/<int:pk>/', views.VoteEditViewSet.as_view(), name='votes_edit'),
    # DELETE
    path('api/delete/poll/<int:pk>/', views.PollsDeleteViewSet.as_view(), name='poll_delete'),
    path('api/delete/choice/<int:pk>/', views.ChoiceDestroyViewSet.as_view(), name='choice_delete'),
    path('api/delete/vote/<int:pk>/', views.VoteDestroyViewSet.as_view(), name='vote_delete'),
    
    path('api/retrieve/<int:pk>/', views.ChoiceRetrieveViewSet.as_view(), name='detail'),
]
