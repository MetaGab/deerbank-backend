from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from accounts.views import * 

router = DefaultRouter()
router.register("clients", ClientViewSet)
router.register("accounts", AccountViewSet)
router.register("cards", CardViewSet)
router.register("branches", BranchViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('login/',
        AuthTokenView.as_view(),
        name='login'),
    path('verify/',
        VerifyAuthTokenView.as_view(),
        name='verify'),
    path('logout/',
        LogoutUserAPIView.as_view(),
        name='logout'),
]
