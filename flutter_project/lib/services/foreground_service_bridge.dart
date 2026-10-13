// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella
//
// Dart controller for SaphiraForegroundService.
// Channel: com.saphira.ai/background_service

import 'package:flutter/services.dart';

class SaphiraForegroundServiceBridge {
  static const MethodChannel _channel =
      MethodChannel('com.saphira.ai/background_service');

  /// Starts the Saphira Foreground Service to hold persistent WebSockets and audio.
  static Future<bool> startService() async {
    try {
      final bool success = await _channel.invokeMethod('startService');
      return success;
    } on PlatformException catch (e) {
      print('[Saphira Engine Error] Failed to start foreground service: ${e.message}');
      return false;
    }
  }

  /// Stops the active foreground service.
  static Future<bool> stopService() async {
    try {
      final bool success = await _channel.invokeMethod('stopService');
      return success;
    } on PlatformException catch (e) {
      print('[Saphira Engine Error] Failed to stop foreground service: ${e.message}');
      return false;
    }
  }

  /// Prompts system settings to grant SYSTEM_ALERT_WINDOW (floating overlay) permission.
  static Future<bool> requestOverlayPermission() async {
    try {
      final bool hasPermission =
          await _channel.invokeMethod('requestOverlayPermission');
      return hasPermission;
    } on PlatformException catch (e) {
      print('[Saphira Engine Error] Overlay permission request failed: ${e.message}');
      return false;
    }
  }

  /// Returns whether the overlay permission is currently granted.
  static Future<bool> canDrawOverlays() async {
    try {
      return await _channel.invokeMethod<bool>('canDrawOverlays') ?? false;
    } on PlatformException {
      return false;
    }
  }
}
