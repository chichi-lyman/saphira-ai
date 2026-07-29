// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// MethodChannel bridge: Android VoiceInteractionSession → open Saphira overlay

import 'package:flutter/services.dart';

typedef OverlayOpener = void Function(Map<dynamic, dynamic>? args);

class AssistantChannel {
  static const MethodChannel _channel =
      MethodChannel('com.saphira.ai/assistant');

  static void bind({required OverlayOpener onOpenOverlay}) {
    _channel.setMethodCallHandler((call) async {
      if (call.method == 'openOverlay') {
        final args = call.arguments is Map
            ? Map<dynamic, dynamic>.from(call.arguments as Map)
            : null;
        onOpenOverlay(args);
      }
    });
  }
}
