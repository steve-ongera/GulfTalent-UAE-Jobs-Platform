from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('auth/login/',   views.AdminLoginView.as_view(),  name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(),      name='token-refresh'),
    path('auth/logout/',  views.AdminLogoutView.as_view(), name='logout'),
    path('auth/me/',      views.AdminMeView.as_view(),     name='me'),

    # ── Categories (public) ───────────────────────────────────────────────────
    path('categories/',                         views.CategoryListView.as_view(),      name='category-list'),
    path('categories/<slug:slug>/',             views.CategoryDetailView.as_view(),    name='category-detail'),
    path('categories/<slug:slug>/documents/',   views.CategoryDocumentsView.as_view(), name='category-documents'),

    # ── Jobs (public) ─────────────────────────────────────────────────────────
    path('jobs/',              views.JobListView.as_view(),     name='job-list'),
    path('jobs/featured/',     views.FeaturedJobsView.as_view(), name='job-featured'),
    path('jobs/<slug:slug>/',  views.JobDetailView.as_view(),   name='job-detail'),

    # ── Applications (public submit) ──────────────────────────────────────────
    path('applications/', views.ApplicationSubmitView.as_view(), name='application-submit'),

    # ── Admin — Categories ────────────────────────────────────────────────────
    path('admin/categories/',        views.AdminCategoryListCreateView.as_view(), name='admin-category-list'),
    path('admin/categories/<int:pk>/', views.AdminCategoryDetailView.as_view(),  name='admin-category-detail'),

    # ── Admin — Required Documents ────────────────────────────────────────────
    path('admin/documents/',         views.AdminDocumentListCreateView.as_view(), name='admin-document-list'),
    path('admin/documents/<int:pk>/', views.AdminDocumentDetailView.as_view(),   name='admin-document-detail'),

    # ── Admin — Jobs ──────────────────────────────────────────────────────────
    path('admin/jobs/',                          views.AdminJobListCreateView.as_view(),    name='admin-job-list'),
    path('admin/jobs/<int:pk>/',                 views.AdminJobDetailView.as_view(),        name='admin-job-detail'),
    path('admin/jobs/<int:pk>/toggle-featured/', views.AdminJobToggleFeaturedView.as_view(), name='admin-job-featured'),
    path('admin/jobs/<int:pk>/toggle-active/',   views.AdminJobToggleActiveView.as_view(),  name='admin-job-active'),

    # ── Admin — Applications ──────────────────────────────────────────────────
    path('admin/applications/',                  views.AdminApplicationListView.as_view(),   name='admin-app-list'),
    path('admin/applications/export/',           views.AdminApplicationExportView.as_view(), name='admin-app-export'),
    path('admin/applications/<int:pk>/',         views.AdminApplicationDetailView.as_view(), name='admin-app-detail'),
    path('admin/applications/<int:pk>/status/',  views.AdminApplicationStatusView.as_view(), name='admin-app-status'),

    # ── Admin — Dashboard ─────────────────────────────────────────────────────
    path('admin/dashboard/stats/', views.AdminDashboardStatsView.as_view(), name='admin-stats'),
]