from django.urls import path
from django.views.decorators.cache import cache_page

from mailings.views import IndexView, RecipientCreateView, RecipientListView, RecipientDeleteView, RecipientDetailView, \
    RecipientUpdateView
from mailings.apps import MailingsConfig

app_name = MailingsConfig.name

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path('/recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('/recipients/', RecipientListView.as_view(), name='recipients'),
    path('/recipients/<int:pk>/confirm_delete/', RecipientDeleteView.as_view(), name='recipient_confirm_delete'),
    path('/recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('/recipients/<int:pk>/edit', RecipientUpdateView.as_view(), name='recipient_update'),

    #     path("contacts/", TemplateView.as_view(), name="contacts"),
    #     path("product/<int:pk>/", cache_page(60)(DetailView.as_view()), name="product"),
    #     path("product/new/", CreateView.as_view(), name="product_create"),
    #     path("product/<int:pk>/edit/", UpdateView.as_view(), name="product_edit"),
    #     path("product/<int:pk>/confirm_delete/", DeleteView.as_view(), name="product_confirm_delete"),
    #     path("product/<int:pk>/unpublish/", UnpublishView.as_view(), name="unpublish_product"),
]
