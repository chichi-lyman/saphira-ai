// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// MethodChannel: Android VoiceInteractionService / session → Flutter overlay

import 'package:flutter/services.dart';

typedef OverlayOpener = void Function(Map<dynamic, dynamic>? args);

class AssistantChannel {
  static const MethodChannel _channel =
      MethodChannel('com.saphira.ai/assistant');

  static OverlayOpener? _onOpenOverlay;

  /// Call once from app bootstrap (e.g. main.dart / home initState).
  static void bind({required OverlayOpener onOpenOverlay}) {
    _onOpenOverlay = onOpenOverlay;
    _channel.setMethodCallHandler((call) async {
      switch (call.method) {
        case 'openOverlay':
          final args = call.arguments is Map
              ? Map<dynamic, dynamic>.from(call.arguments as Map)
              : <dynamic, dynamic>{};
          _onOpenOverlay?.call(args);
          return true;
        default:
          throw PlatformException(
            code: 'unimplemented',
            message: 'Method ${call.method} not implemented',
          );
      }
    });
  }

  /// Optional: Flutter → native (e.g. request end of assistant session).
  static Future<void> notifySessionEnded() async {
    try {
      await _channel.invokeMethod('sessionEnded');
    } on PlatformException catch (e) {
      // Native may not implement yet
      assert(() {
        // ignore: avoid_print
        print('AssistantChannel.sessionEnded: $e');
        return true;
      }());
    }
  }
}
