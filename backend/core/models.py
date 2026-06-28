from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN USER
# ─────────────────────────────────────────────────────────────────────────────
class AdminUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email required')
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = AdminUserManager()

    class Meta:
        verbose_name = 'Admin User'

    def __str__(self):
        return self.email


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=60, blank=True, help_text='Bootstrap icon class e.g. bi-briefcase')
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def job_count(self):
        return self.jobs.filter(is_active=True).count()


# ─────────────────────────────────────────────────────────────────────────────
# REQUIRED DOCUMENT (per category — admin configures)
# ─────────────────────────────────────────────────────────────────────────────
class RequiredDocument(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('image', 'Image (JPG/PNG)'),
        ('doc', 'Word Document'),
        ('any', 'Any'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='required_documents')
    label = models.CharField(max_length=100, help_text='e.g. Passport Copy, CV / Resume')
    description = models.CharField(max_length=255, blank=True)
    accepted_file_types = models.CharField(max_length=20, choices=FILE_TYPES, default='any')
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.category.name} — {self.label}'


# ─────────────────────────────────────────────────────────────────────────────
# JOB
# ─────────────────────────────────────────────────────────────────────────────
class Job(models.Model):
    JOB_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]
    EMIRATES = [
        ('dubai', 'Dubai'),
        ('abu_dhabi', 'Abu Dhabi'),
        ('sharjah', 'Sharjah'),
        ('ajman', 'Ajman'),
        ('umm_al_quwain', 'Umm Al Quwain'),
        ('ras_al_khaimah', 'Ras Al Khaimah'),
        ('fujairah', 'Fujairah'),
    ]
    EXPERIENCE = [
        ('entry', 'Entry Level (0-2 yrs)'),
        ('mid', 'Mid Level (2-5 yrs)'),
        ('senior', 'Senior Level (5-10 yrs)'),
        ('executive', 'Executive (10+ yrs)'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='jobs')
    emirate = models.CharField(max_length=30, choices=EMIRATES, default='dubai')
    location_detail = models.CharField(max_length=150, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE, default='mid')
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_display = models.CharField(max_length=100, blank=True, help_text='e.g. AED 5,000 - 8,000/month')
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    image = models.ImageField(upload_to='jobs/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug, n = base, 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'; n += 1
            self.slug = slug
        if not self.seo_title:
            self.seo_title = f'{self.title} Jobs in {self.get_emirate_display()} | GulfTalent'
        if not self.seo_description:
            self.seo_description = self.description[:157] + '...' if len(self.description) > 160 else self.description
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def application_count(self):
        return self.applications.count()


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class Application(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    NATIONALITIES = [
        ('kenyan', 'Kenyan'), ('ugandan', 'Ugandan'), ('tanzanian', 'Tanzanian'),
        ('rwandan', 'Rwandan'), ('ethiopian', 'Ethiopian'), ('other', 'Other'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    nationality = models.CharField(max_length=20, choices=NATIONALITIES, default='kenyan')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')], blank=True)
    current_location = models.CharField(max_length=150, blank=True)
    cover_letter = models.TextField(blank=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    highest_education = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    admin_notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} → {self.job.title}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


# ─────────────────────────────────────────────────────────────────────────────
# UPLOADED DOCUMENT
# ─────────────────────────────────────────────────────────────────────────────
def doc_upload_path(instance, filename):
    return f'documents/application_{instance.application.id}/{filename}'


class UploadedDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='uploaded_documents')
    required_document = models.ForeignKey(RequiredDocument, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.CharField(max_length=100)
    file = models.FileField(upload_to=doc_upload_path)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.label} — {self.application}'