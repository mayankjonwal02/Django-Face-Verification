from django.contrib import admin
from django.urls import path, include  # Import include function
from libraryApp import urls as library_urls  # Import urls as a separate variable (optional but for clarity)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include(library_urls))  # Use include to reference the libraryApp's URLs
]
