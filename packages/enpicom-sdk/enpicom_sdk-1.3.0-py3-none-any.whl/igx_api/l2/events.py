import json
import uuid
from types import TracebackType
from typing import Any, Callable, Type

from loguru import logger
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from igx_api.l2.client.igx_api_client import IgxApiClient
from igx_api.l2.types.event import Event
from igx_api.l2.types.whoami import Whoami
from igx_api.l2.util.env import get_api_key_or_error, get_event_host, get_event_port, get_event_root_topic

OnEventCallback = Callable[[str, Event], None]
"""Callback function to be called when an event is received.

Args:
    topic (str): The topic on which the event was received.
    event (Event): The event that was received.
"""


# Function hidden from the user, should not be used directly by consumers of the SDK
def _create_paho_client(client_id: str, topic: str | list[str], on_event: OnEventCallback) -> Client:
    logger.debug(f"Listening for events on topic {topic} with client_id {client_id}")

    paho_client = Client(
        client_id=client_id,
        transport="websockets",
        clean_session=False,
        callback_api_version=CallbackAPIVersion.VERSION2,  # Editor says unexpected argument, not true
    )
    paho_client.ws_set_options(headers={"igx-api-key": get_api_key_or_error()}, path="/events")

    # If we are not localhost, we need to call `tls_set`
    if "localhost" not in get_event_host():
        paho_client.tls_set()

    def on_connect(client: Client, _userdata: Any, _connect_flags: ConnectFlags, _reason_code: ReasonCode, _properties: Properties | None = None) -> None:  # type: ignore[misc]
        logger.info("Connected to events endpoint")
        if isinstance(topic, list):
            topics = [(t, 1) for t in topic]
            client.subscribe(topics, qos=1)
        else:
            client.subscribe(topic, qos=1)

    def on_subscribe(_client: Client, _userdata: Any, _mid: int, reason_code_list: list[ReasonCode], _properties: Properties | None = None) -> None:  # type: ignore[misc]
        logger.info(f"Subscribed to topic with QoS {reason_code_list[0]}")

    def on_message(_client: Client, _userdata: Any, message: MQTTMessage) -> None:  # type: ignore[misc]
        # In our case, payload is always a JSON string
        json_payload = json.loads(message.payload.decode("utf-8"))
        # Parse it as our event type
        try:
            event = Event.model_validate(json_payload)
            on_event(message.topic, event)
        except Exception as _e:
            logger.error(f"Failed to parse event: {json.dumps(json_payload)}, not calling callback")

    def on_connect_fail(_client: Client, _userdata: Any) -> None:  # type: ignore[misc]
        # This is also logged when the connection is lost, and it's trying to re-connect.
        logger.warning("Connection failed, retrying...")

    paho_client.on_connect = on_connect
    paho_client.on_message = on_message
    paho_client.on_connect_fail = on_connect_fail
    paho_client.on_subscribe = on_subscribe

    return paho_client


class EventListener:
    """Base event listener class, handles the context managing and client creation.

    **Do not use this class directly, use `UserEventListener`, `SpaceEventListener` or `OrganizationEventListener` instead.**
    """

    _paho_client: Client

    def __init__(self, on_event: OnEventCallback, client_id: str, topic: str | list[str]):
        if type(self) is EventListener:
            raise TypeError("EventListener should not be used directly, use UserEventListener or OrganizationEventListener")

        self._paho_client = _create_paho_client(client_id, topic, on_event)

    def _connect(self) -> None:
        logger.debug("Connecting to events endpoint")

        host = get_event_host()
        port = get_event_port()

        logger.debug(f"Event host: {host}")
        logger.debug(f"Event port: {port}")

        self._paho_client.connect(host, port, 60)

    def __enter__(self) -> None:
        self._connect()
        self._paho_client.loop_start()

    def __exit__(self, exc_type: Type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None) -> None:
        logger.debug("Disconnecting from events endpoint")
        self._paho_client.loop_stop()

    def loop_forever(self) -> None:
        """Start listening for events indefinitely. This will block the main thread."""

        self._connect()

        logger.debug("Listening for events indefinitely")
        self._paho_client.loop_forever()


class UserEventListener(EventListener):
    def __init__(self, on_event: OnEventCallback, client_id: str | None = None):
        """Listen for events on the user level.

        The user that the events are listened for is determined by the API key used.

        This class is a context manager that listens for events on the user level. It will automatically
        subscribe to the correct topic and connect to the endpoint. When an event is received, the provided callback
        function is called with the topic and the event as arguments. When the context manager is exited, the connection
        will be closed automatically.
        When using this as a context manager, the connection will be spawned on a separate thread so the main thread is
        not blocked.

        Alternatively you can use the loop_forever method to keep the connection open indefinitely, keep in mind that
        this will block the main thread.

        Args:
            on_event (OnEventCallback): The callback function to be called when an event is received.
            client_id (str | None): The unique identifier of the client. Defaults to a random UUID. Take care when providing a
              custom client ID, as it must be unique across all clients listening for events. If another script uses
              the same client ID, the other will be disconnected. Defaults to a random UUID.

        Example:
            Using it as a context manager:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            with UserEventListener(on_event=on_event):
                while True:
                    pass
            ```

            Or using it with the `loop_forever` method, in this case, to stop the loop, the script must be interrupted:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            listener = UserEventListener(on_event=on_event)
            listener.loop_forever()
            ```
        """

        # First find out what user you are
        with IgxApiClient() as igx_client:
            whoami: Whoami = igx_client.whoami_api.whoami()
        user_id = whoami.user.id

        client_id = client_id or str(uuid.uuid4())
        client_id = f"{get_event_root_topic()}/{user_id}/{client_id}"
        topic = f"{get_event_root_topic()}/user/{user_id}"

        super().__init__(on_event, client_id, topic)


class SpaceEventListener(EventListener):
    def __init__(self, on_event: OnEventCallback, client_id: str | None = None):
        """Listen for events on the space level.

        The spaces that the events are listened for is determined by the API key used.

        This class is a context manager that listens for events on the space level. It will automatically
        subscribe to the correct topics and connect to the endpoint. When an event is received, the provided callback
        function is called with the topic and the event as arguments. When the context manager is exited, the connection
        will be closed automatically.
        When using this as a context manager, the connection will be spawned on a separate thread so the main thread is
        not blocked.

        Alternatively you can use the loop_forever method to keep the connection open indefinitely, keep in mind that
        this will block the main thread.

        Args:
            on_event (OnEventCallback): The callback function to be called when an event is received.
            client_id (str | None): The unique identifier of the client. Defaults to a random UUID. Take care when providing a
              custom client ID, as it must be unique across all clients listening for events. If another script uses
              the same client ID, the other will be disconnected. Defaults to a random UUID.

        Example:
            Using it as a context manager:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            with SpaceEventListener(on_event=on_event):
                while True:
                    pass
            ```

            Or using it with the `loop_forever` method, in this case, to stop the loop, the script must be interrupted:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            listener = SpaceEventListener(on_event=on_event)
            listener.loop_forever()
            ```
        """

        # First find out which spaces you have access to
        with IgxApiClient() as igx_client:
            whoami: Whoami = igx_client.whoami_api.whoami()
        user_id = whoami.user.id

        client_id = client_id or str(uuid.uuid4())
        client_id = f"{get_event_root_topic()}/{user_id}/{client_id}"
        topics = [f"{get_event_root_topic()}/space/{s.id}" for s in whoami.spaces]

        super().__init__(on_event, client_id, topics)


class OrganizationEventListener(EventListener):
    def __init__(self, on_event: OnEventCallback, client_id: str | None = None):
        """Listen for events on the organization level.

        The organization that the events are listened for is determined by the API key used.

        This class is a context manager that listens for events on the organization level. It will automatically
        subscribe to the correct topic and connect to the endpoint. When an event is received, the provided callback
        function is called with the topic and the event as arguments. When the context manager is exited, the connection
        will be closed automatically.
        When using this as a context manager, the connection will be spawned on a separate thread so the main thread is
        not blocked.

        Alternatively you can use the loop_forever method to keep the connection open indefinitely, keep in mind that
        this will block the main thread.

        Args:
            on_event (OnEventCallback): The callback function to be called when an event is received.
            client_id (str | None): The unique identifier of the client. Defaults to a random UUID. Take care when providing a
              custom client ID, as it must be unique across all clients listening for events. If another script uses
              the same client ID, the other will be disconnected. Defaults to a random UUID.

        Example:
            Using it as a context manager:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            with OrganizationEventListener(on_event=on_event):
                while True:
                    pass
            ```

            Or using it with the `loop_forever` method, in this case, to stop the loop, the script must be interrupted:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            listener = OrganizationEventListener(on_event=on_event)
            listener.loop_forever()
            ```
        """

        # First find out what organization you are
        with IgxApiClient() as igx_client:
            whoami: Whoami = igx_client.whoami_api.whoami()
        user_id = whoami.user.id  # In this case the organization token still has a machine user attached to it
        organization_id = whoami.organization.id

        client_id = client_id or str(uuid.uuid4())
        client_id = f"{get_event_root_topic()}/{user_id}/{client_id}"
        topic = f"{get_event_root_topic()}/organization/{organization_id}"

        super().__init__(on_event, client_id, topic)
