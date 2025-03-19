from enum import Enum
from typing import Any, List, Optional, Union

from flet.core.constrained_control import ConstrainedControl
from flet.core.control import Control, OptionalNumber
from flet.core.ref import Ref
from flet.core.types import ColorEnums, ColorValue

class ContentsAlign(Enum):
    BASIC = "basic"
    REVERSE = "reverse"
    ALTERNATING = "alternating"

class TimelineType(Enum):
    BASIC = "basic"
    STYLE_BASED = "styleBased"

class ConnectorStyle(Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DECORATED = "decorated"

class ConnectionDirection(Enum):
    BEFORE = "before"
    AFTER = "after"

class TimelineNodeAlign(Enum):
    START = "start"
    END = "end"
    BASIC = "basic"

class IndicatorStyle(Enum):
    DOT = "dot"
    OUTLINED = "outlined"
    CONTAINER = "container"
    TRANSPARENT = "transparent"

class Timeline(ConstrainedControl):
    """
    FletTimelines Control implementa il pacchetto timelines di Flutter.
    """

    def __init__(
        self,
        # Control
        ref: Optional[Ref] = None,
        width: OptionalNumber = None,
        height: OptionalNumber = None,
        left: OptionalNumber = None,
        top: OptionalNumber = None,
        right: OptionalNumber = None,
        bottom: OptionalNumber = None,
        expand: Union[None, bool, int] = None,
        opacity: OptionalNumber = None,
        tooltip: Optional[str] = None,
        visible: Optional[bool] = None,
        disabled: Optional[bool] = None,
        data: Any = None,
        #
        # FletTimelines specifico
        #
        items: Optional[List[Control]] = None,
        timeline_type: Optional[TimelineType] = None,
        contents_align: Optional[ContentsAlign] = None,
        color: Optional[ColorValue] = None,
        indicator_size: OptionalNumber = None,
        connector_style: Optional[ConnectorStyle] = None,
        connector_thickness: OptionalNumber = None,
        connector_space: OptionalNumber = None,
        connector_indent: OptionalNumber = None,
        connector_end_indent: OptionalNumber = None,
        indicator_style: Optional[IndicatorStyle] = None,
        indicator_position: OptionalNumber = None,
        node_position: OptionalNumber = None,
        node_align: Optional[TimelineNodeAlign] = None,
        connection_direction: Optional[ConnectionDirection] = None,
        dash_size: OptionalNumber = None,
        gap_size: OptionalNumber = None,
        gap_color: Optional[ColorValue] = None,
    ):

        ConstrainedControl.__init__(
            self,
            ref=ref,
            width=width,
            height=height,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            expand=expand,
            opacity=opacity,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            data=data,
        )

        self.items = items
        self.timeline_type = timeline_type
        self.contents_align = contents_align
        self.color = color
        self.indicator_size = indicator_size
        self.connector_style = connector_style
        self.connector_thickness = connector_thickness
        self.connector_space = connector_space
        self.connector_indent = connector_indent
        self.connector_end_indent = connector_end_indent
        self.indicator_style = indicator_style
        self.indicator_position = indicator_position
        self.node_position = node_position
        self.node_align = node_align
        self.connection_direction = connection_direction
        self.dash_size = dash_size
        self.gap_size = gap_size
        self.gap_color = gap_color

    def _get_control_name(self):
        return "flet_timelines"

    # items
    @property
    def items(self) -> Optional[List[Control]]:
        return self.__items

    @items.setter
    def items(self, value: Optional[List[Control]]):
        self.__items = value

    def _get_children(self):
        result = []
        if self.__items:
            result.extend(self.__items)
        return result

    # timeline_type
    @property
    def timeline_type(self) -> Optional[TimelineType]:
        return self.__timeline_type

    @timeline_type.setter
    def timeline_type(self, value: Optional[TimelineType]):
        self.__timeline_type = value
        if isinstance(value, TimelineType):
            self._set_attr("timelineType", value.value)
        else:
            self._set_attr("timelineType", value)

    # contents_align
    @property
    def contents_align(self) -> Optional[ContentsAlign]:
        return self.__contents_align

    @contents_align.setter
    def contents_align(self, value: Optional[ContentsAlign]):
        self.__contents_align = value
        if isinstance(value, ContentsAlign):
            self._set_attr("contentsAlign", value.value)
        else:
            self._set_attr("contentsAlign", value)

    # color
    @property
    def color(self) -> Optional[ColorValue]:
        return self.__color

    @color.setter
    def color(self, value: Optional[ColorValue]):
        self.__color = value
        self._set_enum_attr("color", value, ColorEnums)

    # indicator_size
    @property
    def indicator_size(self) -> OptionalNumber:
        return self._get_attr("indicatorSize")

    @indicator_size.setter
    def indicator_size(self, value: OptionalNumber):
        self._set_attr("indicatorSize", value)

    @property
    def indicator_style(self) -> Optional[IndicatorStyle]:
        return self.__indicator_style

    @indicator_style.setter
    def indicator_style(self, value: Optional[IndicatorStyle]):
        self.__indicator_style = value
        if isinstance(value, IndicatorStyle):
            self._set_attr("indicatorStyle", value.value)
        else:
            self._set_attr("indicatorStyle", value)

    @property
    def connector_style(self) -> Optional[ConnectorStyle]:
        return self.__connector_style

    @connector_style.setter
    def connector_style(self, value: Optional[ConnectorStyle]):
        self.__connector_style = value
        if isinstance(value, ConnectorStyle):
            self._set_attr("connectorStyle", value.value)
        else:
            self._set_attr("connectorStyle", value)
            
    @property
    def connector_thickness(self) -> OptionalNumber:
        return self._get_attr("connectorThickness")

    @connector_thickness.setter
    def connector_thickness(self, value: OptionalNumber):
        self._set_attr("connectorThickness", value)

    @property
    def connector_space(self) -> OptionalNumber:
        return self._get_attr("connectorSpace")

    @connector_space.setter
    def connector_space(self, value: OptionalNumber):
        self._set_attr("connectorSpace", value)

    @property
    def connector_indent(self) -> OptionalNumber:
        return self._get_attr("connectorIndent")

    @connector_indent.setter
    def connector_indent(self, value: OptionalNumber):
        self._set_attr("connectorIndent", value)

    @property
    def indicator_position(self) -> OptionalNumber:
        return self._get_attr("indicatorPosition")

    @indicator_position.setter
    def indicator_position(self, value: OptionalNumber):
        self._set_attr("indicatorPosition", value)

    @property
    def node_position(self) -> OptionalNumber:
        return self._get_attr("nodePosition")

    @node_position.setter
    def node_position(self, value: OptionalNumber):
        self._set_attr("nodePosition", value)

    @property
    def node_align(self) -> Optional[TimelineNodeAlign]:
        return self.__node_align

    @node_align.setter
    def node_align(self, value: Optional[TimelineNodeAlign]):
        self.__node_align = value
        if isinstance(value, TimelineNodeAlign):
            self._set_attr("nodeAlign", value.value)
        else:
            self._set_attr("nodeAlign", value)

    @property
    def connection_direction(self) -> Optional[ConnectionDirection]:
        return self.__connection_direction

    @connection_direction.setter
    def connection_direction(self, value: Optional[ConnectionDirection]):
        self.__connection_direction = value
        if isinstance(value, ConnectionDirection):
            self._set_attr("connectionDirection", value.value)
        else:
            self._set_attr("connectionDirection", value)

    @property
    def dash_size(self) -> OptionalNumber:
        return self._get_attr("dashSize")

    @dash_size.setter
    def dash_size(self, value: OptionalNumber):
        self._set_attr("dashSize", value)

    @property
    def gap_size(self) -> OptionalNumber:
        return self._get_attr("gapSize")

    @gap_size.setter
    def gap_size(self, value: OptionalNumber):
        self._set_attr("gapSize", value)

    @property
    def gap_color(self) -> Optional[ColorValue]:
        return self.__gap_color

    @gap_color.setter
    def gap_color(self, value: Optional[ColorValue]):
        self.__gap_color = value
        self._set_enum_attr("gapColor", value, ColorEnums)