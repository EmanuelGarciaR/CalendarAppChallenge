from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import ClassVar

from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error


#

# TODO: Implement Reminder class here
@dataclass
class Reminder:
    EMAIL: ClassVar[str] = "email"
    SYSTEM: ClassVar[str] = "system"
    date_time: datetime
    type: str = EMAIL

    def __str__(self):
        return (f"Reminder on {self.date_time} of type {self.type}")


# TODO: Implement Event class here
@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time

    reminders: list[Reminder] = field(default_factory=list)
    id: str = field(default_factory=generate_unique_id)

    def add_reminder(self, date_time, type: str = Reminder.EMAIL):
        remind = Reminder(date_time, type)
        self.reminders.append(remind)

    def delete_reminder(self, reminder_index: int) -> None:
        if 0 <= reminder_index < len(self.reminders):
            del self.reminders[reminder_index]
        else:
            reminder_not_found_error()

    def __str__(self):
        return f"ID: {self.id}\nEvent title: {self.title}\nDescription: {self.description}\nTime: {self.start_at} - {self.end_at}"


# TODO: Implement Day class here
from datetime import time, datetime, timedelta
from app.services.util import slot_not_available_error, event_not_found_error


class Day:
    def __init__(self, date_: date):
        self.date_ = date_
        self.slots: dict[time, str | None] = {}
        self._init_slots()

    def _init_slots(self):
        start_time = time(00, 00)
        end_time = time(23, 45)
        current_time = start_time

        while current_time <= end_time:
            self.slots[current_time] = None
            current_time = (datetime.combine(self.date_, current_time) + timedelta(minutes=15)).time()

    def add_event(self, event_id: str, start_at: time, end_at: time):
        current_time = start_at

        while current_time < end_at:
            if self.slots.get(current_time) is not None:
                slot_not_available_error()
                return

            current_time = (datetime.combine(self.date_, current_time) + timedelta(minutes=15)).time()

        current_time = start_at
        while current_time < end_at:
            self.slots[current_time] = event_id
            current_time = (datetime.combine(self.date_, current_time) + timedelta(minutes=15)).time()

    def delete_event(self, event_id: str):
        deleted = False
        for slot in list(self.slots.keys()):
            if self.slots[slot] == event_id:
                self.slots[slot] = None
                deleted = True

        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        # Remove existing event
        for slot in list(self.slots.keys()):
            if self.slots[slot] == event_id:
                self.slots[slot] = None

        # Check for availability and update
        current_time = start_at
        while current_time < end_at:
            if self.slots.get(current_time) is not None and self.slots[current_time] != event_id:
                slot_not_available_error()
                return
            current_time = (datetime.combine(self.date_, current_time) + timedelta(minutes=15)).time()

        current_time = start_at
        while current_time < end_at:
            self.slots[current_time] = event_id
            current_time = (datetime.combine(self.date_, current_time) + timedelta(minutes=15)).time()


# TODO: Implement Calendar class here
class Calendar:
    def __init__(self):
        self.days: dict[str, Day] = {}
        self.events: dict[str, Event] = {}



    def add_reminder(self, event_id: str, date_time: datetime, type_: str):
        if event_id not in self.events:
            event_not_found_error()
            return

        event = self.events[event_id]
        event.add_reminder(date_time, type_)

    def find_available_slots(self, date_: date) -> list[time]:
        if date_.isoformat() not in self.days:
            return []

        day = self.days[date_.isoformat()]
        available_slots = [slot for slot, event_id in day.slots.items() if event_id is None]
        return available_slots

    def update_event(self, event_id: str, title: str, description: str, date_: date, start_at: time, end_at: time):
        event = self.events[event_id]
        if not event:
            event_not_found_error()

        is_new_date = False

        if event.date_ != date_:
            self.delete_event(event_id)
            event = Event(title=title, description=description, date_=date_, start_at=start_at, end_at=end_at)
            event.id = event_id
            self.events[event_id] = event
            is_new_date = True
            if date_ not in self.days:
                self.days[date_] = Day(date_)
            day = self.days[date_]
            day.add_event(event_id, start_at, end_at)
        else:
            event.title = title
            event.description = description
            event.date_ = date_
            event.start_at = start_at
            event.end_at = end_at

        for day in self.days.values():
            if not is_new_date and event_id in day.slots.values():
                day.delete_event(event.id)
                day.update_event(event.id, start_at, end_at)

    def delete_event(self, event_id: str):
        if event_id not in self.events:
            event_not_found_error()

        self.events.pop(event_id)

        for day in self.days.values():
            if event_id in day.slots.values():
                day.delete_event(event_id)
                break

    def find_events(self, start_at: date, end_at: date) -> dict[date, list[Event]]:
        events: dict[date, list[Event]] = {}
        for event in self.events.values():
            if start_at <= event.date_ <= end_at:
                if event.date_ not in events:
                    events[event.date_] = []
                events[event.date_].append(event)
        return events

    def delete_reminder(self, event_id: str, reminder_index: int):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        event.delete_reminder(reminder_index)

    def list_reminders(self, event_id: str) -> list[Reminder]:
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        return event.reminders
