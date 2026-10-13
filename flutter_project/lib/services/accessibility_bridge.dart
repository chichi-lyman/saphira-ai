// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella

import 'package:flutter/services.dart';

/// Dart-side bridge to [SaphiraAccessibilityService] via MethodChannel.
///
/// Channel: `ai.saphira/accessibility`
///
/// All mutation methods require a prior [authorize] call whose token was
/// issued by the Saphira backend autonomy / policy layer.
class SaphiraAccessibilityBridge {
  static const _channel = MethodChannel('ai.saphira/accessibility');

  /// Returns true when the user has enabled the accessibility service.
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

  /// JSON string of the current window hierarchy (requires auth).
  Future<String> dumpUiTree() async {
    return await _channel.invokeMethod<String>('dumpUiTree') ?? '{}';
  }

  Future<bool> clickByText(String text) async {
    return await _channel.invokeMethod<bool>('clickByText', {'text': text}) ?? false;
  }

  Future<bool> clickByViewId(String viewId) async {
    return await _channel.invokeMethod<bool>('clickByViewId', {'viewId': viewId}) ?? false;
  }

  Future<bool> clickAt(double x, double y) async {
    return await _channel.invokeMethod<bool>('clickAt', {'x': x, 'y': y}) ?? false;
  }

  /// direction: "up" | "down" | "forward" | "backward"
  Future<bool> scroll(String direction) async {
    return await _channel.invokeMethod<bool>('scroll', {'direction': direction}) ?? false;
  }

  Future<bool> setText(String viewId, String text) async {
    return await _channel.invokeMethod<bool>('setText', {
          'viewId': viewId,
          'text': text,
        }) ??
        false;
  }

  /// name: HOME | BACK | RECENTS | NOTIFICATIONS | QUICK_SETTINGS
  Future<bool> globalAction(String name) async {
    return await _channel.invokeMethod<bool>('globalAction', {'name': name}) ?? false;
  }
}
