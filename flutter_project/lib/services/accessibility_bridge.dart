// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella
//
// Dart bridge for com.saphira.ai.SaphiraAccessibilityService
// Channel: com.saphira.ai/accessibility

import 'package:flutter/services.dart';

class SaphiraAccessibilityBridge {
  static const _channel = MethodChannel('com.saphira.ai/accessibility');

  Future<bool> isAvailable() async {
    try {
      return await _channel.invokeMethod<bool>('isAvailable') ?? false;
    } on PlatformException {
      return false;
    }
  }

  /// Supply a short-lived token from the backend policy engine.
  Future<bool> authorize(String token, {int ttlMs = 30000}) async {
    return await _channel.invokeMethod<bool>('authorize', {
          'token': token,
          'ttlMs': ttlMs,
        }) ??
        false;
  }

  Future<void> revokeAuth() async {
    await _channel.invokeMethod('revokeAuth');
  }

  Future<bool> clickElementByText(String text) async {
    return await _channel.invokeMethod<bool>('clickElementByText', {'text': text}) ?? false;
  }

  Future<bool> injectText(String text) async {
    return await _channel.invokeMethod<bool>('injectText', {'text': text}) ?? false;
  }

  Future<bool> tapAt(double x, double y) async {
    return await _channel.invokeMethod<bool>('tapAt', {'x': x, 'y': y}) ?? false;
  }

  /// name: HOME | BACK | RECENTS | NOTIFICATIONS
  Future<bool> globalAction(String name) async {
    return await _channel.invokeMethod<bool>('globalAction', {'name': name}) ?? false;
  }
}
