from . serializers import *
from rest_framework.generics import CreateAPIView,RetrieveAPIView,ListAPIView,UpdateAPIView,DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import status
from django.db import DatabaseError

# Create your views here.

class UserRegisterView(CreateAPIView):
    """API endpoint for user registration."""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self,request,*args, **kwargs):
        try: 
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
    permission_classes = [AllowAny]
    
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
    
    
class UserHomePageView(APIView):
    """API endpoint to display email and username of all users."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserHomeSerializer(user)
        return Response(serializer.data)
    
    
class BlogCreateView(CreateAPIView):
    """API endpoint for creating a new blog."""
    serializer_class = BlogCreateSerializer
    permission_classes = [IsAuthenticated]  

    def create(self, request, *args, **kwargs):
        """Override the create method to handle custom responses."""
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Blog created successfully.", "data": response.data},
            status=status.HTTP_201_CREATED
        )

class BlogUpdateView(UpdateAPIView):
    """API endpoint for updating an existing blog."""
    queryset = Blog.objects.all()
    serializer_class = BlogUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug' 

    def get_queryset(self):
        """Restrict updates to blogs owned by the authenticated user."""
        return Blog.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Override the update method to customize error handling."""
        partial = kwargs.pop('partial', False)  
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data,
            partial=partial
        )
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {"message": "Blog updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Failed to update blog.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class BlogDeleteView(DestroyAPIView):
    """API endpoint for deleting an existing blog."""
    queryset = Blog.objects.all()
    serializer_class = BlogDeleteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  

    def get_queryset(self):
        """Ensure that only blogs belonging to the authenticated user are deletable."""
        return Blog.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Override delete method to customize the response."""
        blog = self.get_object()  
        blog_title = blog.title  
        self.perform_destroy(blog)  
        return Response(
            {
                "message": f"Blog '{blog_title}' deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
        
class BlogListView(ListAPIView):
    """API endpoint to list all blogs with limited data accessible by everyone."""
    queryset = Blog.objects.all().order_by('-created_at')  
    serializer_class = BlogListSerializer
    permission_classes = [AllowAny]
    
              
class AuthenticatedUserBlogListView(ListAPIView):
    """API endpoint to list blogs for the authenticated user."""
    serializer_class = BlogListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return blogs for the authenticated user."""
        return Blog.objects.filter(user=self.request.user).order_by('-created_at')
    
            
class BlogDetailView(RetrieveAPIView):
    """API endpoint for retrieving the details of a specific blog."""
    queryset = Blog.objects.all()  
    serializer_class = BlogDetailSerializer
    permission_classes = [IsAuthenticated]  
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        """Override the GET method to add custom response handling."""
        blog = self.get_object()  
        serializer = self.get_serializer(blog)
        return Response({
            "message": "Blog details fetched successfully.",
            "data": serializer.data
        })
        
           
class UserProfileView(RetrieveAPIView):
    """API endpoint to retrieve user profile details."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve the profile of the logged-in user."""
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            if not profile.profile_picture:
                profile.profile_picture = ""  
            return profile
        except UserProfile.DoesNotExist:
            if not self.request.user.email or not self.request.user.username:
                raise NotFound("User details are incomplete. Please provide email and username.")
            return UserProfile(user=self.request.user, profile_picture="")

    
class UserProfileUpdateView(UpdateAPIView):
    """API view for updating user profile."""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve the logged-in user."""
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Override the update method to customize the response."""
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Failed to update profile.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
        
class UserLogoutView(APIView):
    """API endpoint for user logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Invalidate the access and refresh tokens by blacklisting the refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response({
                "message": "Logout successful."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "Error during logout.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)