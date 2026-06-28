from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import AdminUser, Category, RequiredDocument, Job, Application, UploadedDocument


# ─── Auth ─────────────────────────────────────────────────────────────────────
class AdminLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.full_name
        return token


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'email', 'full_name', 'created_at']
        read_only_fields = ['id', 'created_at']


# ─── Required Document ────────────────────────────────────────────────────────
class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ['id', 'category', 'label', 'description', 'accepted_file_types', 'is_required', 'order']


# ─── Category ─────────────────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    job_count = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()
    required_documents = RequiredDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image_url', 'icon',
            'seo_title', 'seo_description', 'seo_keywords',
            'is_active', 'order', 'job_count', 'required_documents',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        from django.utils.text import slugify
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        from django.utils.text import slugify
        if 'name' in validated_data and validated_data['name'] != instance.name:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().update(instance, validated_data)


# ─── Job ──────────────────────────────────────────────────────────────────────
class JobListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    emirate_display = serializers.CharField(source='get_emirate_display', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)
    experience_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'category_name', 'category_slug',
            'emirate', 'emirate_display', 'location_detail',
            'job_type', 'job_type_display', 'experience_level', 'experience_display',
            'salary_display', 'salary_min', 'salary_max', 'image_url',
            'is_featured', 'is_urgent', 'is_active',
            'seo_title', 'seo_description', 'seo_keywords',
            'created_at', 'expires_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class JobDetailSerializer(JobListSerializer):
    category = CategorySerializer(read_only=True)
    application_count = serializers.ReadOnlyField()

    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + [
            'category', 'description', 'requirements',
            'responsibilities', 'benefits', 'application_count', 'updated_at',
        ]


class AdminJobSerializer(serializers.ModelSerializer):
    application_count = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()
    emirate_display = serializers.CharField(source='get_emirate_display', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ─── Application ──────────────────────────────────────────────────────────────
class UploadedDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedDocument
        fields = ['id', 'label', 'file_url', 'file_name', 'file_size', 'file_type', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ApplicationSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'job', 'first_name', 'last_name', 'email', 'phone',
            'nationality', 'date_of_birth', 'gender', 'current_location',
            'cover_letter', 'years_of_experience', 'highest_education', 'linkedin_url',
        ]

    def validate_email(self, value):
        return value.lower().strip()

    def validate_phone(self, value):
        if len(''.join(filter(str.isdigit, value))) < 9:
            raise serializers.ValidationError('Enter a valid phone number.')
        return value


class ApplicationListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_slug = serializers.CharField(source='job.slug', read_only=True)
    category_name = serializers.CharField(source='job.category.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 'email', 'phone',
            'nationality', 'job_title', 'job_slug', 'category_name',
            'status', 'status_display', 'applied_at', 'updated_at',
        ]


class ApplicationDetailSerializer(ApplicationListSerializer):
    uploaded_documents = UploadedDocumentSerializer(many=True, read_only=True)

    class Meta(ApplicationListSerializer.Meta):
        fields = ApplicationListSerializer.Meta.fields + [
            'date_of_birth', 'gender', 'current_location',
            'cover_letter', 'years_of_experience', 'highest_education',
            'linkedin_url', 'admin_notes', 'ip_address', 'uploaded_documents',
        ]


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status', 'admin_notes']