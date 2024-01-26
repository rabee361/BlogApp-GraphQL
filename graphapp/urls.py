from django.urls import path
from .views import *
from graphene_django.views import GraphQLView
from .schema import schema
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),

]+ static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)