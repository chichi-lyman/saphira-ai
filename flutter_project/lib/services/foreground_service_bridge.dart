// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella
//
// Dart bridge for SaphiraForegroundService + SYSTEM_ALERT_WINDOW permission.
// Channel: com.saphira.ai/service

import 'package:flutter/services.dart';

class SaphiraForegroundServiceBridge {
  static const _channel = MethodChannel('com.saphira.ai/service');

  /// Start the sticky foreground service (persistent notification + mic type).
  Future<bool> start() async {
    try {
      return await _channel.invokeMethod<bool>('startForegroundService') ?? false;
    } on PlatformException catch (e) {
      print('startForegroundService failed: ${e.message}');
      return false;
    }
  }

  /// Stop the foreground service.
  Future<bool> stop() async {
    try {
      return await _channel.invokeMethod<bool>('stopForegroundService') ?? false;
    } on PlatformException catch (e) {
      print('stopForegroundService failed: ${e.message}');
      return false;
    }
  }

  /// Opens system settings for "Display over other apps" if not already granted.
  /// Returns true if permission is already held.
  Future<bool> requestOverlayPermission() async {
    try {
      return await _channel.invokeMethod<bool>('requestOverlayPermission') ?? false;
    } on PlatformException {
      return false;
    }
  }

  /// Check whether SYSTEM_ALERT_WINDOW is currently granted.
  Future<bool> canDrawOverlays() async {
    try {
      return await _channel.invokeMethod<bool>('canDrawOverlays') ?? false;
    } on PlatformException {
      return false;
    }
  }
}
