import 'package:flet/flet.dart';

import 'flet_math.dart';

CreateControlFactory createControl = (CreateControlArgs args) {
  switch (args.control.type) {
    case "flet_math":
      return FletMathControl(
        parent: args.parent,
        control: args.control,
        children: args.children,
        backend: args.backend,
      );
    default:
      return null;
  }
};

void ensureInitialized() {
  // nothing to initialize
}
