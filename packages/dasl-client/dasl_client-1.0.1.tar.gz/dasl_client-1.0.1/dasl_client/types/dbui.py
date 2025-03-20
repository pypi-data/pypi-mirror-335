from typing import Optional, List

from dasl_api import (
    DbuiV1ObservableEventsList,
    DbuiV1ObservableEventsListItemsInnerNotable,
    DbuiV1ObservableEventsListItemsInner,
)
from pydantic import BaseModel


class Dbui(BaseModel):
    class ObservableEvents(BaseModel):
        class Notable(BaseModel):
            id: Optional[str] = None
            rule_name: Optional[str] = None
            summary: Optional[str] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1ObservableEventsListItemsInnerNotable],
            ) -> Optional["Dbui.ObservableEvents.Notable"]:
                if obj is None:
                    return None

                return Dbui.ObservableEvents.Notable(
                    id=obj.id, rule_name=obj.rule_name, summary=obj.summary
                )

        class Event(BaseModel):
            var_from: Optional[str] = None
            adjust_by: Optional[float] = None
            notable: Optional["Dbui.ObservableEvents.Notable"] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1ObservableEventsListItemsInner],
            ) -> Optional["Dbui.ObservableEvents.Event"]:
                if obj is None:
                    return None

                return Dbui.ObservableEvents.Event(
                    var_from=obj.var_from,
                    adjust_by=obj.adjust_by,
                    notable=Dbui.ObservableEvents.Notable.from_api_obj(obj.notable),
                )

        class EventsList(BaseModel):
            cursor: Optional[str] = None
            items: List["Dbui.ObservableEvents.Event"] = []

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1ObservableEventsList],
            ) -> Optional["Dbui.ObservableEvents.EventsList"]:
                if obj is None:
                    return None

                return Dbui.ObservableEvents.EventsList(
                    cursor=obj.cursor,
                    items=[
                        Dbui.ObservableEvents.Event.from_api_obj(item)
                        for item in obj.items
                    ],
                )
