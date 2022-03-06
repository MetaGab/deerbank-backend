from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from transactions.views import * 

router = DefaultRouter()
router.register("transactions", TransactionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('transfer/',
        PerformTransfer.as_view(),
        name='transfer'),
    path('deposit/',
        PerformDeposit.as_view(),
        name='deposit'),
    path('withdraw/',
        PerformWithdrawal.as_view(),
        name='withdraw'),
]
