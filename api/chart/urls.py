from django.urls import path
from .views import (
    SellSumView, SellNerkhView, SellCartView, TicketsView, NesbatView, Moghayerat, CardShakhsi, TekListView,
    NahyeListView, GSListView, Ipclog_list_View, TicketHourView, AverageTicketsView, SumTicketsMountView,
    SellAllProductView
)

urlpatterns = [
    path("sum_sell_view/<int:id>/", SellSumView.as_view()),
    path("sum_nerkh_view/<int:id>/", SellNerkhView.as_view()),
    path("sum_cart_view/<int:id>/", SellCartView.as_view()),
    path("ticket_view/<int:id>/", TicketsView.as_view()),
    path("nesbat_view/<int:id>/", NesbatView.as_view()),
    path("Moghayerat/", Moghayerat.as_view()),
    path("CardShakhsi/", CardShakhsi.as_view()),
    path("tek-list_view/", TekListView.as_view()),
    path("nahye-list_view/", NahyeListView.as_view()),
    path("gs-list_view/", GSListView.as_view()),
    path("ipclog-list_view/", Ipclog_list_View.as_view()),
    path("ticket_hour_view/", TicketHourView.as_view()),
    path("average_ticket_view/", AverageTicketsView.as_view()),
    path("sum_ticket_mount_view/", SumTicketsMountView.as_view()),
    path("sell_all_product_view/<int:id>/", SellAllProductView.as_view()),
]
