import uuid

import pydantic


def mk_uuid() -> pydantic.UUID4:
    return uuid.uuid4()


def mk_short_uuid_str(existing_uuid: uuid.UUID | None = None) -> str:
    return (existing_uuid or mk_uuid()).hex[:12]
