from django.urls import path
from .views import ParticipantLocationListView, participant_sos_view

urlpatterns = [
    path('activities/<uuid:activity_id>/participants/locations/', ParticipantLocationListView.as_view(), name='participant-locations'),
    path('activities/<uuid:activity_id>/sos/', participant_sos_view, name='participant-sos'),
]
