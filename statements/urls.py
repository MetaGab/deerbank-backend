from django.urls import path
from statements.views import * 


urlpatterns = [
    path('current-ammount/',
        GetCurrentAmmount.as_view(),
        name='current-ammount'),
    path('statement/',
        GetStatement.as_view(),
        name='statement'),
]
