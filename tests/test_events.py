from __future__ import annotations

import pytest

from traffic_agent.events import (
    ALL_TOPICS,
    EVENT_TRAFFIC,
    EVENT_TRANSFORM_APPLIED,
    EventBus,
    Event,
)


def test_publish_delivers_to_topic_subscribers():
    bus = EventBus()
    got = []
    bus.subscribe(EVENT_TRAFFIC, got.append)
    delivered = bus.publish(Event(EVENT_TRAFFIC, {"n": 1}))
    assert delivered == 1
    assert len(got) == 1
    assert got[0].payload == {"n": 1}


def test_publish_wildcard_receives_all():
    bus = EventBus()
    got = []
    bus.subscribe(ALL_TOPICS, got.append)
    bus.publish(Event(EVENT_TRAFFIC))
    bus.publish(Event(EVENT_TRANSFORM_APPLIED))
    assert len(got) == 2


def test_publish_counts_topic_plus_wildcard():
    bus = EventBus()
    bus.subscribe(EVENT_TRAFFIC, lambda e: None)
    bus.subscribe(ALL_TOPICS, lambda e: None)
    assert bus.publish(Event(EVENT_TRAFFIC)) == 2


def test_unsubscribe_stops_delivery():
    bus = EventBus()
    got = []
    unsub = bus.subscribe(EVENT_TRAFFIC, got.append)
    bus.publish(Event(EVENT_TRAFFIC))
    unsub()
    bus.publish(Event(EVENT_TRAFFIC))
    assert len(got) == 1


def test_unsubscribe_twice_is_safe():
    bus = EventBus()
    got = []
    unsub = bus.subscribe(EVENT_TRAFFIC, got.append)
    unsub()
    unsub()  # 第二次不应抛错
    bus.publish(Event(EVENT_TRAFFIC))
    assert got == []


def test_handler_exception_recorded_not_raised():
    bus = EventBus()
    ok = []
    bus.subscribe(EVENT_TRAFFIC, lambda e: 1 / 0)
    bus.subscribe(EVENT_TRAFFIC, ok.append)
    delivered = bus.publish(Event(EVENT_TRAFFIC))
    assert delivered == 1
    assert len(bus.errors) == 1
    assert "ZeroDivisionError" in bus.errors[0]["error"]
    assert bus.errors[0]["topic"] == EVENT_TRAFFIC
    assert len(ok) == 1


def test_history_and_topic_filter():
    bus = EventBus()
    bus.publish(Event(EVENT_TRAFFIC, {"i": 1}))
    bus.publish(Event(EVENT_TRANSFORM_APPLIED, {"i": 2}))
    bus.publish(Event(EVENT_TRAFFIC, {"i": 3}))
    traffic = bus.events(topic=EVENT_TRAFFIC)
    assert [e.payload["i"] for e in traffic] == [1, 3]
    assert len(bus.events()) == 3
    assert len(bus.events(topic=EVENT_TRANSFORM_APPLIED)) == 1
    assert bus.events(limit=2)[0].payload["i"] == 1


def test_history_limit_evicts_oldest():
    bus = EventBus(history_limit=3)
    for i in range(5):
        bus.publish(Event(EVENT_TRAFFIC, {"i": i}))
    events = bus.events()
    assert len(events) == 3
    assert [e.payload["i"] for e in events] == [2, 3, 4]


def test_events_negative_limit_raises():
    bus = EventBus()
    with pytest.raises(ValueError):
        bus.events(limit=-1)


def test_publish_non_event_raises():
    bus = EventBus()
    with pytest.raises(TypeError):
        bus.publish("not-an-event")


def test_subscribe_empty_topic_raises():
    bus = EventBus()
    with pytest.raises(ValueError):
        bus.subscribe("", lambda e: None)


def test_subscribe_non_callable_raises():
    bus = EventBus()
    with pytest.raises(TypeError):
        bus.subscribe(EVENT_TRAFFIC, "nope")


def test_history_limit_must_be_positive():
    with pytest.raises(ValueError):
        EventBus(history_limit=0)
    with pytest.raises(ValueError):
        EventBus(history_limit=-5)


def test_clear():
    bus = EventBus()
    bus.publish(Event(EVENT_TRAFFIC))
    bus.subscribe(EVENT_TRAFFIC, lambda e: 1 / 0)
    bus.publish(Event(EVENT_TRAFFIC))
    assert len(bus.events()) == 2
    assert len(bus.errors) == 1
    bus.clear()
    assert bus.events() == []
    assert bus.errors == []


def test_event_defaults():
    e = Event(EVENT_TRAFFIC)
    assert e.payload == {}
    assert e.ts > 0
    e2 = Event(EVENT_TRAFFIC, payload={"a": 1})
    assert e2.payload == {"a": 1}
