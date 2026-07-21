from django.db.models import Count, Exists, OuterRef, QuerySet
from .models import Activity, ActivityRole, Participant

def get_activities_for_user(*, user) -> QuerySet[Activity]:
    return (
        Activity.objects.filter(
            Exists(Participant.objects.filter(activity_id=OuterRef('pk'), user=user))
        )
        .annotate(participant_count=Count('participants', distinct=True))
        .distinct()
    )

def get_activity_roles(*, activity: Activity) -> QuerySet[ActivityRole]:
    return ActivityRole.objects.filter(activity=activity)
