import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:timelines_plus/timelines_plus.dart';

class FletTimelinesControl extends StatelessWidget {
  final Control? parent;
  final Control control;
  final List<Control> children;
  final bool parentDisabled;
  final FletControlBackend backend;

  const FletTimelinesControl({
    super.key,
    required this.parent,
    required this.control,
    required this.children,
    required this.parentDisabled,
    required this.backend,
  });

  @override
  Widget build(BuildContext context) {
    debugPrint("Timeline build: ${control.id} (${control.hashCode})");
    bool disabled = control.isDisabled || parentDisabled;
    
    // Get timeline properties
    var timelineType = control.attrString("timelineType", "basic");
    var contentsAlign = control.attrString("contentsAlign", "alternating");
    var color = control.attrColor("color", context);
    var indicatorSize = control.attrDouble("indicatorSize") ?? 20.0;
    
    // New properties
    var connectorStyle = control.attrString("connectorStyle", "solidLine");
    var connectorThickness = control.attrDouble("connectorThickness") ?? 2.0;
    var connectorSpace = control.attrDouble("connectorSpace") ?? 4.0;
    var connectorIndent = control.attrDouble("connectorIndent") ?? 0.0;
    var connectorEndIndent = control.attrDouble("connectorEndIndent") ?? 0.0;
    var indicatorStyle = control.attrString("indicatorStyle", "dot");
    var indicatorPosition = control.attrDouble("indicatorPosition") ?? 0.5;
    var nodePosition = control.attrDouble("nodePosition") ?? 0.5;
    var nodeAlign = control.attrString("nodeAlign", "basic");
    var connectionDirection = control.attrString("connectionDirection", "after");
    var dashSize = control.attrDouble("dashSize") ?? 4.0;
    var gapSize = control.attrDouble("gapSize") ?? 4.0;
    var gapColor = control.attrColor("gapColor", context);
    
    var timelineItems = children.where((c) => c.isVisible).toList();
    
    Widget timelineWidget;
    
    if (timelineType == "styleBased") {
      timelineWidget = _buildStyledTimeline(
        timelineItems,
        contentsAlign,
        color,
        indicatorSize,
        connectorStyle,
        connectorThickness,
        connectorSpace,
        connectorIndent,
        connectorEndIndent,
        indicatorStyle,
        indicatorPosition,
        nodePosition,
        nodeAlign,
        connectionDirection,
        dashSize,
        gapSize,
        gapColor,
        context,
        disabled,
      );
    } else {
      timelineWidget = _buildBasicTimeline(
        timelineItems,
        contentsAlign,
        color,
        indicatorSize,
        context,
        disabled,
      );
    }

    return constrainedControl(context, timelineWidget, parent, control);
  }

  Widget _buildBasicTimeline(
    List<Control> items,
    String? contentsAlignStr,
    Color? color,
    double indicatorSize,
    BuildContext context,
    bool disabled,
  ) {
    // Determina l'allineamento dei contenuti
    ContentsAlign contentsAlign;
    switch (contentsAlignStr) {
      case "basic":
        contentsAlign = ContentsAlign.basic;
        break;
      case "reverse":
        contentsAlign = ContentsAlign.reverse;
        break;
      case "alternating":
        contentsAlign = ContentsAlign.alternating;
        break;
      default:
        contentsAlign = ContentsAlign.alternating;
    }

    // Costruisci la timeline
    return FixedTimeline.tileBuilder(
      builder: TimelineTileBuilder.fromStyle(
        contentsAlign: contentsAlign,
        contentsBuilder: (context, index) {
          if (index < items.length) {
            var item = items[index];
            return Padding(
              padding: const EdgeInsets.all(8.0),
              child: createControl(control, item.id, disabled),
            );
          }
          return null;
        },
        indicatorStyle: IndicatorStyle.dot,
        itemCount: items.length,
        indicatorPositionBuilder: (context, index) => 0.5,
      ),
    );
  }

  Widget _buildStyledTimeline(
    List<Control> items,
    String? contentsAlignStr,
    Color? color,
    double indicatorSize,
    String? connectorStyleStr,
    double connectorThickness,
    double connectorSpace,
    double connectorIndent,
    double connectorEndIndent,
    String? indicatorStyleStr,
    double indicatorPosition,
    double nodePosition,
    String? nodeAlignStr,
    String? connectionDirectionStr,
    double dashSize,
    double gapSize,
    Color? gapColor,
    BuildContext context,
    bool disabled,
  ) {
    ContentsAlign contentsAlign = _parseContentsAlign(contentsAlignStr);
    
    // Parse indicator style
    IndicatorStyle getIndicatorStyle() {
      switch (indicatorStyleStr) {
        case "outlined":
          return IndicatorStyle.outlined;
        case "container":
          return IndicatorStyle.container;
        case "transparent":
          return IndicatorStyle.transparent;
        default:
          return IndicatorStyle.dot;
      }
    }

    // Parse connector style
    ConnectorStyle getConnectorStyle() {
      switch (connectorStyleStr) {
        case "dashedLine":
          return ConnectorStyle.dashedLine;
        case "transparent":
          return ConnectorStyle.transparent;
        default:
          return ConnectorStyle.solidLine;
      }
    }

    // Parse connection direction
    ConnectionDirection direction = connectionDirectionStr == "before" 
        ? ConnectionDirection.before 
        : ConnectionDirection.after;

    return FixedTimeline.tileBuilder(
      builder: TimelineTileBuilder.connectedFromStyle(
        contentsAlign: contentsAlign,
        oppositeContentsBuilder: (context, index) => _buildOppositeContents(items[index], disabled),
        contentsBuilder: (context, index) => _buildContents(items[index], disabled),
        indicatorStyleBuilder: (context, index) => getIndicatorStyle(),
        connectorStyleBuilder: (context, index) => getConnectorStyle(),
        connectionDirection: direction,
        itemCount: items.length,
        indicatorPositionBuilder: (context, index) => indicatorPosition,
        nodePositionBuilder: (context, index) => nodePosition,
        firstConnectorStyle: getConnectorStyle(),
        lastConnectorStyle: getConnectorStyle(),
      ),
      theme: TimelineThemeData(
        color: color,
        indicatorTheme: IndicatorThemeData(
          size: indicatorSize,
          position: indicatorPosition,
        ),
        connectorTheme: ConnectorThemeData(
          thickness: connectorThickness,
          space: connectorSpace,
          indent: connectorIndent,
        ),
      ),
    );
  }

  ContentsAlign _parseContentsAlign(String? alignStr) {
    switch (alignStr) {
      case "basic":
        return ContentsAlign.basic;
      case "reverse":
        return ContentsAlign.reverse;
      case "alternating":
        return ContentsAlign.alternating;
      default:
        return ContentsAlign.alternating;
    }
  }

  Widget? _buildContents(Control item, bool disabled) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: createControl(control, item.id, disabled),
    );
  }

  Widget? _buildOppositeContents(Control item, bool disabled) {
    var oppositeContentId = item.attrString("oppositeContentId", "");
    if (oppositeContentId != null && oppositeContentId.isNotEmpty) {
      return Padding(
        padding: const EdgeInsets.all(8.0),
        child: createControl(control, oppositeContentId, disabled),
      );
    }
    return null;
  }
}