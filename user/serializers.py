from . models import CustomUser,Blog,UserProfile
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


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
    """Serializer for displaying email, username and profile picture on the homepage."""
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_picture']

    def get_profile_picture(self, obj):
        """Retrieve the user's profile picture from the UserProfile model."""
        profile = obj.User_profile.first() 
        return profile.profile_picture if profile else None
        
        
class BlogCreateSerializer(serializers.ModelSerializer):
    """Serializer for Blog model."""
    user = serializers.StringRelatedField(read_only=True) 
    slug = serializers.SlugField(read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    reading_time = serializers.IntegerField(read_only=True) 
    
    class Meta:
        model = Blog
        fields = ['id', 'user', 'title', 'description', 'media', 'tags', 'reading_time', 'created_at', 'updated_at', 'slug']
        read_only_fields = ['created_at', 'updated_at', 'slug', 'reading_time']
        
    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        """Ensure description is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value
    
    def validate_tags(self, value):
        """Validate and handle the tags input."""
        if value is None:  
            return []
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list or a single string.")        
        if any(not isinstance(tag, str) for tag in value):
            raise serializers.ValidationError("Each tag must be a string.")
        return value

    
    def validate_media(self, value):
        """Validate that media is a list of valid URLs."""
        url_validator = URLValidator()
        if isinstance(value, str):  
            value = [value]
        elif not isinstance(value, list): 
            raise serializers.ValidationError("Media should be a list of URLs.")
        
        if not value:  
            raise serializers.ValidationError("Media cannot be empty.")
        
        for url in value:
            if not isinstance(url, str):
                raise serializers.ValidationError("Each media item must be a valid URL string.")
            try:
                url_validator(url)  
            except ValidationError:
                raise serializers.ValidationError(f"Invalid URL: {url}")
        return value

    def create(self, validated_data):
        """Create a new blog for the logged-in user."""
        validated_data['user'] = self.context['request'].user  
        return super().create(validated_data)

class BlogUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an existing blog."""
    slug = serializers.SlugField(read_only=True)  
    user = serializers.StringRelatedField(read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    ) 

    class Meta:
        model = Blog
        fields = ['id', 'user', 'title', 'description', 'media', 'tags', 'created_at', 'updated_at', 'slug']
        read_only_fields = ['created_at', 'updated_at', 'slug']
        
    def validate_title(self, value):
        """Ensure title is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        """Ensure description is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value
    
    def validate_tags(self, value):
        """Validate and handle the tags input."""
        if isinstance(value, str):
            value = [value]  
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list or a single string.")
        if any(not isinstance(tag, str) for tag in value):
            raise serializers.ValidationError("Each tag must be a string.")
        return value

    def validate_media(self, value):
        """Validate that media is a list of valid URLs."""
        url_validator = URLValidator()
        if isinstance(value, str):  
            value = [value]
        elif not isinstance(value, list):
            raise serializers.ValidationError("Media should be a list of URLs.")
        
        for url in value:
            if not isinstance(url, str):
                raise serializers.ValidationError("Each media item must be a valid URL string.")
            try:
                url_validator(url)
            except ValidationError:
                raise serializers.ValidationError(f"Invalid URL: {url}")
        return value


class BlogDeleteSerializer(serializers.ModelSerializer):
    """Serializer for deleting an existing blog."""
    class Meta:
        model = Blog
        fields = ['id', 'title', 'user']  
        read_only_fields = ['id', 'title', 'user']
        

class BlogListSerializer(serializers.ModelSerializer):
    """Serializer for listing blog titles, one image, and a short description."""
    first_image = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'first_image', 'short_description', 'tags', 'reading_time', 'user_name', 'user_profile_picture', 'created_at', 'updated_at', 'slug']
    
    def get_first_image(self, obj):
        """Return the first image URL from the media field (if available)."""
        if isinstance(obj.media, list) and obj.media:
            return obj.media[0]  
        return None

    def get_short_description(self, obj):
        description_words = obj.description.split()  
        short_desc = ' '.join(description_words[:17])  
        return short_desc
    
    def get_user_profile_picture(self, obj):
        """Retrieve the user's profile picture."""
        profile = UserProfile.objects.filter(user=obj.user).first()
        return profile.profile_picture if profile else None
    
class BlogDetailSerializer(serializers.ModelSerializer):
    """Serializer to return the details of a blog."""
    slug = serializers.SlugField(read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ['id', 'user_name', 'user_profile_picture', 'title', 'description', 'media', 'tags', 'reading_time', 'created_at', 'updated_at', 'slug']
        read_only_fields = ['id', 'user', 'title', 'description', 'media', 'created_at', 'tags', 'reading_time', 'updated_at', 'slug']

    def get_user_profile_picture(self, obj):
        """Retrieve the user's profile picture."""
        profile = UserProfile.objects.filter(user=obj.user).first()
        return profile.profile_picture if profile else None

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer to return user profile details."""
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'username', 'profile_picture']

        
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    email = serializers.EmailField(required=True, validators=[validate_email])
    username = serializers.CharField(max_length=33, required=False)
    profile_picture = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'profile_picture']
    
    def validate_username(self, value):
        """Ensure username is not empty and unique."""
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        """Ensure email is unique."""
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def update(self, instance, validated_data):
        """Update the user and profile information."""
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        
        profile_data = validated_data.get('profile_picture', None)
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.profile_picture = profile_data
            profile.save()
        
        return instance