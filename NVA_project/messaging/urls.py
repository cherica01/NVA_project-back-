from django.urls import path
from .views import (
    ConversationListView, ConversationCreateView, ConversationDetailView,
    MessageListView, MessageDetailView, MessageAttachmentView,
    UnreadMessagesCountView, SearchConversationsView
)

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/create/', ConversationCreateView.as_view(), name='conversation-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('messages/<int:message_id>/attachments/', MessageAttachmentView.as_view(), name='message-attachment'),
    path('unread-count/', UnreadMessagesCountView.as_view(), name='unread-messages-count'),
    path('search/', SearchConversationsView.as_view(), name='search-conversations'),
]