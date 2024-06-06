from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import timedelta
from django.utils import timezone
from rest_framework.throttling import UserRateThrottle
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .serializers import CustomUserSerializer, UserSearchSerializer, FriendRequestSerializer
from .models import CustomUser, FriendRequest

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_staff = True
            
            user.save()
            return Response({
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSearchPagination(PageNumberPagination):
    page_size = 10

class SearchUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if '@' in query:
            
            users = CustomUser.objects.filter(email__icontains=query)
        else:
            
            starting_with_query = CustomUser.objects.filter(name__istartswith=query)
            containing_query = CustomUser.objects.filter(Q(name__icontains=query) & ~Q(name__istartswith=query))
            users = list(starting_with_query) + list(containing_query)

        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendFriendRequestThrottle(UserRateThrottle):
    rate = '3/minute'

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [SendFriendRequestThrottle]

    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user_id')
        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(
            from_user=from_user,
            timestamp__gte=one_minute_ago
        )

        if recent_requests.count() >= 3:
            return Response({'detail': 'You can only send 3 friend requests per minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'detail': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({'detail': 'Friend request sent'}, status=status.HTTP_201_CREATED)

class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        friend_request_id = request.data.get('friend_request_id')
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.to_user != request.user:
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({'detail': 'Friend request accepted'}, status=status.HTTP_200_OK)

class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        friend_request_id = request.data.get('friend_request_id')
        friend_request = FriendRequest.objects.get(id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        friend_request.status = 'rejected'
        friend_request.save()
        return Response({'detail': 'Friend request rejected'}, status=status.HTTP_200_OK)

class ListFriendsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSearchSerializer

    def get_queryset(self):
        user = self.request.user
        friends = CustomUser.objects.filter(
            Q(from_user__to_user=user, from_user__status='accepted') |
            Q(to_user__from_user=user, to_user__status='accepted')
        )
        return friends

class ListPendingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user, status='pending')
