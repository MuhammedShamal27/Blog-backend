from . serializers import *
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import DatabaseError

# Create your views here.

class UserRegisterView(CreateAPIView):
    """API endpoint for user registration."""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self,request,*args, **kwargs):
        try: 
            # serializer = self.get_serializer(data=request.data)
            # serializer.is_valid(raise_exception=True)
            # self.perform_create(serializer)
            response = super().create(request, *args, **kwargs)
            return Response(
                {"message": "User Registered Successfully."},
                status=status.HTTP_201_CREATED
            )
        except DatabaseError as db_error:
            return Response(
                {"error":"An unexpected database error occured.","details": str(db_error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error":"An unexpected error occurred.","details": str(e)},
            )
            
        
class UserLoginView(APIView):
    """API endpoint for user login."""
    
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            login_data = serializer.validated_data
            user = login_data['user']
            access_token = login_data['access_token']
            refresh_token = login_data['refresh_token']
            
            return Response({
                'message': 'Login successful.',
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)     
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    