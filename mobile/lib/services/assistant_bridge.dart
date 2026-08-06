// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Bidirectional MethodChannel bridge between Flutter and the Kotlin
// VoiceInteractionService / MainActivity layer.

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

typedef OverlayCallback = void Function(Map<String, dynamic> args);
typedef ListeningCallback = void Function(bool active);

class AssistantBridge {
  static const String channelName = 'com.saphira.ai/assistant';

  static final AssistantBridge instance = AssistantBridge._();
  AssistantBridge._();

  final MethodChannel _channel = const MethodChannel(channelName);

  OverlayCallback? onOpenOverlay;
  ListeningCallback? onListeningChanged;
  VoidCallback? onSessionEnded;

  bool _initialized = false;

  void init() {
    if (_initialized) return;
    _initialized = true;
    _channel.setMethodCallHandler(_handleNativeCall);
    debugPrint('AssistantBridge: channel ready ($channelName)');
  }

  Future<dynamic> _handleNativeCall(MethodCall call) async {
    debugPrint('AssistantBridge \u2190 native: ${call.method} ${call.arguments}');

    switch (call.method) {
      case 'openOverlay':
        final args = _asMap(call.arguments);
        onOpenOverlay?.call(args);
        return true;
      case 'setListening':
        final active = call.arguments == true ||
            (call.arguments is Map && (call.arguments as Map)['active'] == true);
        onListeningChanged?.call(active);
        return true;
      case 'sessionEnded':
        onSessionEnded?.call();
        return true;
      default:
        debugPrint('AssistantBridge: unhandled method ${call.method}');
        return null;
    }
  }

  Future<bool> startListening({String source = 'flutter'}) async {
    try {
      final result = await _channel.invokeMethod<bool>('startListening', {
        'source': source,
      });
      return result ?? false;
    } on PlatformException catch (e) {
      debugPrint('AssistantBridge startListening error: ${e.message}');
      return false;
    }
  }

  Future<bool> stopListening() async {
    try {
      final result = await _channel.invokeMethod<bool>('stopListening');
      return result ?? false;
    } on PlatformException catch (e) {
      debugPrint('AssistantBridge stopListening error: ${e.message}');
      return false;
    }
  }

  Future<void> notifyOverlayReady() async {
    try {
      await _channel.invokeMethod('overlayReady');
    } on PlatformException catch (e) {
      debugPrint('AssistantBridge overlayReady error: ${e.message}');
    }
  }

  Future<void> endSession() async {
    try {
      await _channel.invokeMethod('endSession');
    } on PlatformException catch (e) {
      debugPrint('AssistantBridge endSession error: ${e.message}');
    }
  }

  Map<String, dynamic> _asMap(dynamic value) {
    if (value is Map) {
      return value.map((k, v) => MapEntry(k.toString(), v));
    }
    return <String, dynamic>{};
  }
}
