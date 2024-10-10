from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from myapp.Models import Client
from myapp.serializers.userSerializer import UserCreateSerializer, ClientSerializer  # Ensure you import ClientSerializer
from myapp.permissions import IsAdminOrOwner
from rest_framework.permissions import IsAuthenticated


class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'destroy', 'update', 'partial_update']:
            self.permission_classes = [IsAdminOrOwner]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAdminOrOwner]
        return super().get_permissions()

    def list(self, request):
        users = Client.objects.all()
        serializer = ClientSerializer(users, many=True)  # Use ClientSerializer here
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            user = Client.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            serializer = ClientSerializer(user)  # Use ClientSerializer here
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            user = Client.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            serializer = UserCreateSerializer(user.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            user = Client.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Client.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            user = Client.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            
            # Check if the request is to change the user's admin status
            if request.user.is_staff and 'is_staff' in request.data:
                if request.data['is_staff'] and not request.user.is_superuser:
                    return Response({'detail': 'Only superusers can grant admin privileges.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Perform the partial update
            serializer = UserCreateSerializer(user.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
