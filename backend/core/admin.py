from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AdminUser, Category, RequiredDocument, Job, Application, UploadedDocument


@admin.register(AdminUser)
class AdminUserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'is_active', 'is_staff', 'created_at']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'full_name', 'password1', 'password2')}),
    )
    search_fields = ['email', 'full_name']


class RequiredDocumentInline(admin.TabularInline):
    model = RequiredDocument
    extra = 1
    fields = ['label', 'description', 'accepted_file_types', 'is_required', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'job_count', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RequiredDocumentInline]


@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = ['label', 'category', 'accepted_file_types', 'is_required', 'order']
    list_filter = ['category', 'is_required']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'emirate', 'job_type', 'is_featured', 'is_active', 'application_count', 'created_at']
    list_filter = ['is_active', 'is_featured', 'is_urgent', 'emirate', 'job_type', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'application_count']
    fieldsets = (
        ('Job Info', {'fields': ('title', 'slug', 'category', 'image')}),
        ('Location', {'fields': ('emirate', 'location_detail')}),
        ('Details', {'fields': ('job_type', 'experience_level', 'salary_min', 'salary_max', 'salary_display')}),
        ('Content', {'fields': ('description', 'requirements', 'responsibilities', 'benefits')}),
        ('Flags', {'fields': ('is_active', 'is_featured', 'is_urgent', 'expires_at')}),
        ('SEO', {'fields': ('seo_title', 'seo_description', 'seo_keywords')}),
        ('Meta', {'fields': ('created_at', 'updated_at', 'application_count')}),
    )


class UploadedDocumentInline(admin.TabularInline):
    model = UploadedDocument
    extra = 0
    readonly_fields = ['label', 'file', 'file_name', 'file_size', 'file_type', 'uploaded_at']
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'job', 'status', 'applied_at']
    list_filter = ['status', 'nationality', 'job__category', 'job__emirate']
    search_fields = ['first_name', 'last_name', 'email', 'job__title']
    list_editable = ['status']
    readonly_fields = ['applied_at', 'updated_at', 'ip_address']
    inlines = [UploadedDocumentInline]
    fieldsets = (
        ('Applicant', {'fields': ('first_name', 'last_name', 'email', 'phone', 'nationality', 'date_of_birth', 'gender', 'current_location')}),
        ('Application', {'fields': ('job', 'cover_letter', 'years_of_experience', 'highest_education', 'linkedin_url')}),
        ('Admin', {'fields': ('status', 'admin_notes')}),
        ('Meta', {'fields': ('applied_at', 'updated_at', 'ip_address')}),
    )