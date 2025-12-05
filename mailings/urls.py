from django.urls import path
from django.views.decorators.cache import cache_page

from mailings.apps import MailingsConfig

# from catalog.views import

app_name = MailingsConfig.name

urlpatterns = [
    #     path("", ListView.as_view(), name="home"),
    #     path("contacts/", TemplateView.as_view(), name="contacts"),
    #     path("product/<int:pk>/", cache_page(60)(DetailView.as_view()), name="product"),
    #     path("product/new/", CreateView.as_view(), name="product_create"),
    #     path("product/<int:pk>/edit/", UpdateView.as_view(), name="product_edit"),
    #     path("product/<int:pk>/confirm_delete/", DeleteView.as_view(), name="product_confirm_delete"),
    #     path("product/<int:pk>/unpublish/", UnpublishView.as_view(), name="unpublish_product"),
]
