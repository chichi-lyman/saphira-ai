// Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
// All rights reserved.

import 'package:flutter/services.dart';

/// MethodChannel bridge for SYSTEM_ALERT_WINDOW permission and floating HUD
/// visibility control (native side: [com.saphira.ai/overlay_hud]).
class SaphiraOverlayHUDBridge {
  static const MethodChannel _channel =
      MethodChannel('com.saphira.ai/overlay_hud');

  /// Verifies if SYSTEM_ALERT_WINDOW permission is granted.
  static Future<bool> checkPermission() async {
    try {
      final bool hasPermission =
          await _channel.invokeMethod('checkOverlayPermission');
      return hasPermission;
    } on PlatformException catch (e) {
      // ignore: avoid_print
      print('[Saphira HUD Error] Failed to check permission: ${e.message}');
      return false;
    }
  }

  /// Launches Android System Settings to grant draw-over-apps permission.
  static Future<bool> requestPermission() async {
    try {
      final bool granted =
          await _channel.invokeMethod('requestOverlayPermission');
      return granted;
    } on PlatformException catch (e) {
      // ignore: avoid_print
      print('[Saphira HUD Error] Failed to request permission: ${e.message}');
      return false;
    }
  }

  /// Toggles floating status bubble visibility over active Android applications.
  static Future<bool> setHUDVisible(bool visible) async {
    try {
      final bool success = await _channel
          .invokeMethod('toggleHUDVisibility', {'visible': visible});
      return success;
    } on PlatformException catch (e) {
      // ignore: avoid_print
      print('[Saphira HUD Error] Failed to set visibility: ${e.message}');
      return false;
    }
  }
}
