import 'package:flet/flet.dart';

import 'flet_timelines.dart';

CreateControlFactory createControl = (CreateControlArgs args) {
  switch (args.control.type) {
    case "flet_timelines":
      return FletTimelinesControl(
        parent: args.parent,
        control: args.control,
        children: args.children,
        backend: args.backend,
        parentDisabled: args.parentDisabled,
      );
    default:
      return null;
  }
};

void ensureInitialized() {
  // nothing to initialize
}
