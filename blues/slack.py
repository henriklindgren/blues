# coding=utf-8
"""
Slack Blueprint
===============

**Fabric environment:**

.. code-block:: yaml

    settings:
      slack:
        # Single config:
        endpoint: https://hooks.slack.com/... # (Required)
        channels:                             # (Required)
          - "#deploy"
        username: deploybot
        icon_emoji: ":rocket"

        # Multiple configs:
        # - endpoint: https://hooks.slack.com/...  # (Required)
        #   channels:                              # (Required)
        #     - "#deploy"
        #   username: deploybot
        #   icon_emoji: ":rocket"
        # - ...

"""
from fabric.utils import warn
from refabric.contrib import blueprints
import urllib2
import json

blueprint = blueprints.get(__name__)


def notify(msg, attachment=None, quiet=True):
    slack_config = blueprint.get('')

    if isinstance(slack_config, dict):
        slack_config = [slack_config]

    for config in slack_config:
        notify_with_config(msg, attachment, config, quiet)


def notify_with_config(msg, attachment, config, quiet):
    channels = config.get('channels', [])
    channel = config.get('channel', None)

    # If channel is specified, add it to channels, and then run it through an
    # OrderedDict, removing any duplicates.
    if channel:
        channels.append(channel)

    if not channels:
        warn('Empty slack channel list, skipping notification')
        return False

    username = config.get('username', 'deploybot')
    icon_emoji = config.get('icon_emoji', ':rocket:')

    endpoint = config.get('endpoint')
    if not endpoint:
        warn('No slack API endpoint found, skipping notification')
        return False

    for channel in set(channels):
        send_request(endpoint=endpoint, channel=channel, username=username,
                     msg=msg, attachment=attachment, icon_emoji=icon_emoji, quiet=quiet)


def send_request(endpoint, channel, username, msg, attachment, icon_emoji, quiet=True):
    data = {
        "channel": channel,
        "username": username,
        "text": msg,
        "icon_emoji": icon_emoji,
    }

    if attachment:
        data["attachments"] = [attachment, ]

    req = urllib2.Request(endpoint, json.dumps(data), {'Content-Type': 'application/json'})
    try:
        urllib2.urlopen(req).close()

    except Exception as e:
        if quiet:
            warn(e)
        else:
            raise
