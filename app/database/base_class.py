from typing import Any
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    id: Any

    def as_dict(self):
        return dict((c.name,
                     getattr(self, c.name))
                    for c in self.__table__.columns)
