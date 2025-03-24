from django.urls import path
from .views import (
    ConversationListView,
    ConversationCreateView,
    ConversationDetailView,
    MessageListView,
    MessageDetailView,
    UnreadMessagesCountView,
    SearchConversationsView,
    CurrentUserView,
    UsersListView,
    AgentsListView,
    AdminsListView
)

urlpatterns = [
    # Conversations
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/create/', ConversationCreateView.as_view(), name='conversation-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    
    # Messages
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    
    # Compteur de messages non lus
    path('unread-count/', UnreadMessagesCountView.as_view(), name='unread-messages-count'),
    
    # Recherche
    path('search/', SearchConversationsView.as_view(), name='search-conversations'),
    
    # Utilisateurs (déplacés de accounts/urls.py vers ici)
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
    path('users/', UsersListView.as_view(), name='users-list'),
    path('agents/', AgentsListView.as_view(), name='agents-list'),
    path('admins/', AdminsListView.as_view(), name='admins-list'),
]

