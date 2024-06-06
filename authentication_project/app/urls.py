from django.urls import path
from . import views
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('search/', views.SearchUsersAPIView.as_view(), name='user-search'),
    path('friends/', views.ListFriendsView.as_view(), name='friends'),
    path('friend-request/pending/', views.ListPendingRequestsView.as_view(), name='pending-friend-requests'),
    path('friend-request/send/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/accept/', views.AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-request/reject/', views.RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
]

