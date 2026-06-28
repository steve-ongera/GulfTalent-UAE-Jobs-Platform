import csv
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import AdminUser, Category, RequiredDocument, Job, Application, UploadedDocument
from .serializers import (
    AdminLoginSerializer, AdminUserSerializer,
    CategorySerializer, RequiredDocumentSerializer,
    JobListSerializer, JobDetailSerializer, AdminJobSerializer,
    ApplicationSubmitSerializer, ApplicationListSerializer,
    ApplicationDetailSerializer, ApplicationStatusSerializer,
    UploadedDocumentSerializer,
)
from .filters import JobFilter, ApplicationFilter
from .email_service import send_application_received, send_status_update


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
class AdminLoginView(TokenObtainPairView):
    serializer_class = AdminLoginSerializer


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data.get('refresh')).blacklist()
            return Response({'detail': 'Logged out.'})
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class AdminMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(AdminUserSerializer(request.user).data)


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIES — Public
# ─────────────────────────────────────────────────────────────────────────────
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class CategoryDocumentsView(generics.ListAPIView):
    """Return required documents for a category (used to build apply form dynamically)."""
    serializer_class = RequiredDocumentSerializer

    def get_queryset(self):
        cat = generics.get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return RequiredDocument.objects.filter(category=cat)


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORIES — Admin
# ─────────────────────────────────────────────────────────────────────────────
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


# ─────────────────────────────────────────────────────────────────────────────
# REQUIRED DOCUMENTS — Admin
# ─────────────────────────────────────────────────────────────────────────────
class AdminDocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = RequiredDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = RequiredDocument.objects.select_related('category')
        cat = self.request.query_params.get('category')
        if cat:
            qs = qs.filter(category_id=cat)
        return qs


class AdminDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer
    permission_classes = [IsAuthenticated]


# ─────────────────────────────────────────────────────────────────────────────
# JOBS — Public
# ─────────────────────────────────────────────────────────────────────────────
class JobListView(generics.ListAPIView):
    queryset = Job.objects.filter(is_active=True).select_related('category')
    serializer_class = JobListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'category__name', 'location_detail']
    ordering_fields = ['created_at', 'title', 'salary_min']
    ordering = ['-is_featured', '-created_at']


class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.filter(is_active=True).select_related('category')
    serializer_class = JobDetailSerializer
    lookup_field = 'slug'


class FeaturedJobsView(generics.ListAPIView):
    serializer_class = JobListSerializer

    def get_queryset(self):
        return Job.objects.filter(is_active=True, is_featured=True).select_related('category')[:6]


# ─────────────────────────────────────────────────────────────────────────────
# JOBS — Admin
# ─────────────────────────────────────────────────────────────────────────────
class AdminJobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all().select_related('category').order_by('-created_at')
    serializer_class = AdminJobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'category__name']


class AdminJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = AdminJobSerializer
    permission_classes = [IsAuthenticated]


class AdminJobToggleFeaturedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job = generics.get_object_or_404(Job, pk=pk)
        job.is_featured = not job.is_featured
        job.save(update_fields=['is_featured'])
        return Response({'is_featured': job.is_featured})


class AdminJobToggleActiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job = generics.get_object_or_404(Job, pk=pk)
        job.is_active = not job.is_active
        job.save(update_fields=['is_active'])
        return Response({'is_active': job.is_active})


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATIONS — Public submit (no auth required)
# ─────────────────────────────────────────────────────────────────────────────
class ApplicationSubmitView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ApplicationSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        application = serializer.save(ip_address=self._get_ip(request))

        for key, file in request.FILES.items():
            if file.size > settings.MAX_UPLOAD_SIZE:
                continue
            label = request.data.get(f'{key}_label', file.name)
            req_doc_id = None
            if key.startswith('doc_') and not key.startswith('doc_extra_'):
                try:
                    req_doc_id = int(key.replace('doc_', ''))
                except ValueError:
                    pass
            req_doc = RequiredDocument.objects.filter(pk=req_doc_id).first() if req_doc_id else None
            UploadedDocument.objects.create(
                application=application, required_document=req_doc,
                label=label, file=file, file_name=file.name,
                file_size=file.size, file_type=file.content_type,
            )

        try:
            send_application_received(application)
        except Exception:
            pass

        return Response({
            'detail': 'Application submitted. Check your email for confirmation.',
            'application_id': application.id,
            'applicant_name': application.full_name,
        }, status=status.HTTP_201_CREATED)

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATIONS — Admin
# ─────────────────────────────────────────────────────────────────────────────
class AdminApplicationListView(generics.ListAPIView):
    queryset = Application.objects.all().select_related('job', 'job__category').order_by('-applied_at')
    serializer_class = ApplicationListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ['first_name', 'last_name', 'email', 'job__title']
    ordering_fields = ['applied_at', 'status', 'first_name']


class AdminApplicationDetailView(generics.RetrieveAPIView):
    queryset = Application.objects.all().prefetch_related('uploaded_documents')
    serializer_class = ApplicationDetailSerializer
    permission_classes = [IsAuthenticated]


class AdminApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        application = generics.get_object_or_404(Application, pk=pk)
        old_status = application.status
        serializer = ApplicationStatusSerializer(application, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        if old_status != application.status:
            try:
                send_status_update(application)
            except Exception:
                pass
        return Response(ApplicationDetailSerializer(application, context={'request': request}).data)


class AdminApplicationExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ApplicationFilter(request.GET, queryset=Application.objects.select_related('job', 'job__category')).qs
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="gulftalent_applications.csv"'
        w = csv.writer(response)
        w.writerow(['ID','First Name','Last Name','Email','Phone','Nationality',
                    'Job Title','Category','Emirate','Status','Yrs Experience','Education','Applied At'])
        for a in qs:
            w.writerow([a.id, a.first_name, a.last_name, a.email, a.phone,
                        a.get_nationality_display(), a.job.title, a.job.category.name,
                        a.job.get_emirate_display(), a.get_status_display(),
                        a.years_of_experience, a.highest_education,
                        a.applied_at.strftime('%Y-%m-%d %H:%M')])
        return response


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD STATS — Admin
# ─────────────────────────────────────────────────────────────────────────────
class AdminDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        return Response({
            'jobs': {
                'total': Job.objects.count(),
                'active': Job.objects.filter(is_active=True).count(),
                'featured': Job.objects.filter(is_featured=True).count(),
            },
            'categories': {
                'total': Category.objects.count(),
                'active': Category.objects.filter(is_active=True).count(),
            },
            'applications': {
                'total': Application.objects.count(),
                'pending': Application.objects.filter(status='pending').count(),
                'reviewed': Application.objects.filter(status='reviewed').count(),
                'shortlisted': Application.objects.filter(status='shortlisted').count(),
                'rejected': Application.objects.filter(status='rejected').count(),
                'hired': Application.objects.filter(status='hired').count(),
                'last_7_days': Application.objects.filter(applied_at__gte=now - timedelta(days=7)).count(),
                'last_30_days': Application.objects.filter(applied_at__gte=now - timedelta(days=30)).count(),
            },
        })