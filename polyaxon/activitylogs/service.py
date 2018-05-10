from event_manager.event_service import EventService
from activitylogs.manager import default_manager


class ActivityLogService(EventService):
    event_manager = default_manager

    def __init__(self):
        self.activity_log = None

    def record_event(self, event):
        assert event.actor_id is not None
        return self.activity_log.objects.create(
            event_type=event.event_type,
            actor_id=event.data[event.actor_id],
            context=event.data,
            created_at=event.datetime,
            content_object=event.instance,
        )

    def setup(self):
        # Load default event types
        import activitylogs.events  # noqa
        from activitylogs.models import ActivityLog

        self.activity_log = ActivityLog