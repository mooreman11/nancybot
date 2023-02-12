from django.urls import path

from tradetracking import views

urlpatterns = [
    # path('congress/<str:firstname>/<str:firstname>', views.),
    path('update-data', views.UpdateStockData.as_view()),
    # path('pelosi-data', views.CongressionalStock.as_view()),
    path('positions/congressman/<str:first>/<str:last>', views.GetPersonsData.as_view()),
    path('trades/congressman/<str:first>/<str:last>', views.GetPersonsData.as_view())
]
