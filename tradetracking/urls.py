from django.urls import path

from tradetracking import views

urlpatterns = [
    # path('congress/<str:firstname>/<str:firstname>', views.),
    path('update-data', views.UpdateStockData.as_view()),
    path('pelosi-data', views.CongressionalStock.as_view()),
]
