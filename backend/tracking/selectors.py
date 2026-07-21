from .models import ParticipantLocation

def get_participant_locations_for_activity(activity_id):
    return ParticipantLocation.objects.filter(
        participant__activity_id=activity_id
    ).select_related(
        'participant', 
        'participant__user', 
        'participant__role'
    )
