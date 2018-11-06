from collections import namedtuple

from constants import user_system
from constants.urls import API_V1
from event_manager import event_subjects
from libs import unique_urls
from libs.http import add_notification_referrer_param, absolute_uri


class EventItemContextSpec(namedtuple('EventItemContextSpec', 'name url object_id')):
    pass


class EventContextSpec(
    namedtuple(
        'EventItemContextSpec',
        'subject_action subject action actor_context object_context datetime')):
    pass


def get_event_subject(event_type):
    """Return the first part of the event_type

    e.g.

    >>> Event.event_type = 'experiment.deleted'
    >>> Event.get_event_subject() == 'experiment'
    """
    return event_type.split('.')[0]


def get_event_action(event_type):
    """Return the second part of the event_type

    e.g.

    >>> Event.event_type = 'experiment.deleted'
    >>> Event.get_event_action() == 'deleted'
    """
    return event_type.split('.')[1]


def get_event_actor_context(event):
    if not event.actor:
        return None

    username = event.data.get(event.actor_name)
    if username is None:
        return None
    if username == user_system.USER_SYSTEM_NAME:
        return EventItemContextSpec(name=username, url='/', object_id=None)
    return EventItemContextSpec(name=username,
                                url=unique_urls.get_user_url(username),
                                object_id=None)


def get_event_object_context(event_content_object, event_type):
    # Deleted objects don't have a content object any more
    if not event_content_object:
        return EventItemContextSpec(name=None, url=None, object_id=None)

    event_subject = get_event_subject(event_type)

    object_id = None
    object_url = None
    object_name = None
    if hasattr(event_content_object, 'id'):
        object_id = event_content_object.id

    if hasattr(event_content_object, 'unique_name'):
        object_name = event_content_object.unique_name
        if event_subject == event_subjects.PROJECT:
            object_url = unique_urls.get_project_url(object_name)
        elif event_subject == event_subjects.EXPERIMENT:
            object_url = unique_urls.get_experiment_url(object_name)
        elif event_subject == event_subjects.EXPERIMENT_GROUP:
            object_url = unique_urls.get_experiment_group_url(object_name)
        elif event_subject == event_subjects.BUILD_JOB:
            object_url = unique_urls.get_build_url(object_name)
        elif event_subject == event_subjects.JOB:
            object_url = unique_urls.get_job_url(object_name)

    elif hasattr(event_content_object, 'name'):
        object_name = event_content_object.name
    elif hasattr(event_content_object, 'username'):
        object_name = event_content_object.username
        object_url = unique_urls.get_user_url(event_content_object.username)

    # Set proper url
    object_url = absolute_uri('{}/app{}'.format(API_V1, object_url))
    return EventItemContextSpec(name=object_name, url=object_url, object_id=object_id)


def get_event_context(event):
    subject = get_event_subject(event_type=event.event_type)
    action = get_event_action(event_type=event.event_type)
    actor_context = get_event_actor_context(event=event)
    object_context = get_event_object_context(
        event_content_object=event.instance,
        event_type=event.event_type)
    return EventContextSpec(subject_action='{} {}'.format(subject, action),
                            subject=subject,
                            action=action,
                            actor_context=actor_context,
                            object_context=object_context,
                            datetime=event.datetime)


def get_readable_event(event_context):
    description = '{} on {}'.format(event_context.subject_action, event_context.datetime)
    if event_context.actor_context:
        description += '\nActor: [{}](/app{})'.format(
            event_context.actor_context.name,
            event_context.actor_context.url,
        )

    if event_context.object_context.name and event_context.object_context.url:
        description += '\nObject: [{}](/app{})'.format(
            event_context.object_context.name,
            event_context.object_context.url,
        )

    return description
