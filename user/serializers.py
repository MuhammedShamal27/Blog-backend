from . models import CustomUser
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""
    password = serializers.CharField(write_only=True)  
    confirm_password = serializers.CharField(write_only=True)  
    class Meta:
        model = CustomUser
        fields = ["email","username","password","confirm_password"]
        
    def validate(self, data):
        """Validate email and username are unique and passwords match."""
        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        if CustomUser.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data
    
    
    def create(self,validated_data):
        """Create a new user after validation."""
        validated_data.pop('confirm_password')
        return CustomUser.objects.create_user(
            email = validated_data['email'],
            username = validated_data['username'],
            password = validated_data['password'],
        )
        
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ["email","password"]
        
    def validate(self,data):
        """Validating is the user exists or not."""
        
        user = authenticate(username=data['email'], password=data['password'])
        print('the user is :',user)
        if user is None:
            raise serializers.ValidationError({"details": "Invalid email or password."})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "This user is blocked. Please contact support."})
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': str(refresh)
        }
    

class UserHomeSerializer(serializers.ModelSerializer):
    """Serializer for displaying email and username on the homepage."""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email']