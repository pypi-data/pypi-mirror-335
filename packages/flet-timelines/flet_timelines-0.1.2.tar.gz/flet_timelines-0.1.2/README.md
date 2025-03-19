# flet-timelines
A powerful Timeline control for Flet that allows you to create beautiful, customizable timelines in your Flet applications.

## Features
- Multiple timeline types (Basic and Style-Based)
- Various content alignments (Basic, Reverse, Alternating)
- Customizable indicators and connectors
- Flexible styling options
- Responsive design

## Installation

Add dependency to `pyproject.toml` of your Flet app:

```toml
dependencies = [
    "flet-timelines",
    "flet>=0.27.6",
]
```

## Basic Usage

Here's a simple example of how to create a basic timeline:

```python
from flet_timelines import Timeline, TimelineType, ContentsAlign
import flet as ft

def main(page: ft.Page):
    # Create timeline items
    items = [
        ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Event 1", weight="bold"),
                        ft.Text("Description of event 1")
                    ]),
                    padding=10
                )
            ),
            width=200
        ),
        ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Event 2", weight="bold"),
                        ft.Text("Description of event 2")
                    ]),
                    padding=10
                )
            ),
            width=200
        )
    ]

    # Create timeline
    timeline = Timeline(
        items=items,
        timeline_type=TimelineType.BASIC,
        contents_align=ContentsAlign.BASIC,
        color=ft.colors.BLUE,
        indicator_size=20,
        expand=True
    )

    page.add(timeline)

ft.app(main)
```

## Timeline Types

### Basic Timeline
The basic timeline provides a simple, clean layout with customizable indicators and connectors.

```python
Timeline(
    items=items,
    timeline_type=TimelineType.BASIC,
    contents_align=ContentsAlign.BASIC
)
```

### Style-Based Timeline
The style-based timeline offers advanced styling options for indicators, connectors, and spacing.

```python
Timeline(
    items=items,
    timeline_type=TimelineType.STYLE_BASED,
    contents_align=ContentsAlign.ALTERNATING,
    connector_style=ConnectorStyle.DASHED,
    indicator_style=IndicatorStyle.OUTLINED
)
```

## Content Alignment

- `ContentsAlign.BASIC`: Items aligned on one side
- `ContentsAlign.REVERSE`: Items aligned on the opposite side
- `ContentsAlign.ALTERNATING`: Items alternate between sides

## API Reference

### Timeline Properties

#### Basic Properties
- `items`: List of Control objects to display in the timeline
- `timeline_type`: Type of timeline (TimelineType.BASIC or TimelineType.STYLE_BASED)
- `contents_align`: Alignment of timeline items (ContentsAlign.BASIC, REVERSE, or ALTERNATING)
- `color`: Color of the timeline indicators and connectors
- `indicator_size`: Size of the timeline indicators

#### Style-Based Properties
- `connector_style`: Style of connectors (ConnectorStyle.SOLID, DASHED, or DECORATED)
- `connector_thickness`: Thickness of connector lines
- `connector_space`: Space between connector and content
- `connector_indent`: Indentation of connectors
- `indicator_style`: Style of indicators (IndicatorStyle.DOT, OUTLINED, CONTAINER, or TRANSPARENT)
- `indicator_position`: Position of indicators
- `node_position`: Position of nodes
- `node_align`: Alignment of nodes (TimelineNodeAlign.START, END, or BASIC)
- `connection_direction`: Direction of connections (ConnectionDirection.BEFORE or AFTER)
- `dash_size`: Size of dashes in dashed connector style
- `gap_size`: Size of gaps between dashes
- `gap_color`: Color of gaps in dashed connector style

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
