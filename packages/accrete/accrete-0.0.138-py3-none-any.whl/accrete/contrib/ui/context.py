import logging
import re
from dataclasses import dataclass, field
from django.core import paginator
from django.db.models import QuerySet, Model
from .filter import Filter

_logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class BaseContext:

    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        for key, value in self.extra.items():
            setattr(self, key, value)

    def dict(self):
        return {
            attr: getattr(self, attr, None) for attr
            in filter(lambda x: not x.startswith('_'), self.__dict__)
        }


@dataclass(kw_only=True)
class Context(BaseContext):

    title: str = ''


@dataclass
class ListContext(Context):

    page: paginator.Page
    queryset: QuerySet
    endless_scroll: bool = True
    detail_enabled: bool = True
    filter: Filter = None
    column_count: int = 1
    column_height: int = 150
    column_height_unit: str = 'px'

    def __post_init__(self):
        super().__post_init__()
        if self.column_count not in range(1, 13):
            _logger.warning(
                'ListContext parameter column_count should be in range 1 - 12'
            )


@dataclass
class ListUpdateContext(BaseContext):

    object: Model
    template: str


@dataclass
class TableContext(Context):

    object_label: str
    fields: list[str]
    page: paginator.Page
    queryset: QuerySet
    footer: dict = field(default_factory=dict)
    endless_scroll: bool = True
    detail_enabled: bool = True
    filter: Filter = None


@dataclass
class TableRowContext(BaseContext):

    object: Model
    fields: list[str]
    queryset: QuerySet
    footer: dict = field(default_factory=dict)


@dataclass
class ModalContext(BaseContext):

    title: str
    modal_id: str
    blocking: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.modal_id = re.sub(r'[^A-Za-z-]+', '', self.modal_id).strip('-')


@dataclass(kw_only=True)
class OobContext(BaseContext):

    template: str
    id: str = None
    swap: str = 'true'
    tag: str = 'div'

    def dict(self) -> dict:
        res = {
            attr: getattr(self, attr, None) for attr
            in filter(
                lambda x:
                not x.startswith('_')
                and x not in ['template', 'id', 'swap', 'tag'],
                self.__dict__
            )
        }
        res.update({'oob': {
            'template': self.template,
            'id': self.id,
            'swap': self.swap,
            'tag': self.tag
        }})
        return res
