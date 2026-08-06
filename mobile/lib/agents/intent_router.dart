// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Intent router — maps phrases to Android actions before LLM fallback.

import 'android_action_agent.dart';

enum SaphiraIntent {
  chat, call, sms, alarm, openApp, navigation, weather, volume,
  flashlight, wifi, bluetooth, settings, search, unknown,
}

class RoutedIntent {
  final SaphiraIntent intent;
  final Map<String, String> slots;
  final String original;
  const RoutedIntent({required this.intent, required this.slots, required this.original});
}

class IntentRouter {
  static final IntentRouter instance = IntentRouter._();
  IntentRouter._();

  RoutedIntent route(String raw) {
    final text = raw.trim().toLowerCase();
    if (text.isEmpty) return RoutedIntent(intent: SaphiraIntent.chat, slots: {}, original: raw);

    final callMatch = RegExp(r'(?:call|dial|phone)\s+(.+)').firstMatch(text);
    if (callMatch != null) {
      return RoutedIntent(intent: SaphiraIntent.call, slots: {'contact': callMatch.group(1)!.trim()}, original: raw);
    }
    final smsMatch = RegExp(r'(?:text|sms|message)\s+(\w+)(?:\s+(.+))?').firstMatch(text);
    if (smsMatch != null) {
      return RoutedIntent(intent: SaphiraIntent.sms, slots: {
        'contact': smsMatch.group(1)!,
        if (smsMatch.group(2) != null) 'body': smsMatch.group(2)!.trim(),
      }, original: raw);
    }
    final alarmMatch = RegExp(r'(?:set\s+)?(?:an?\s+)?alarm\s+(?:for\s+)?(.+)').firstMatch(text);
    if (alarmMatch != null || text.contains('set alarm')) {
      return RoutedIntent(intent: SaphiraIntent.alarm, slots: {'time': alarmMatch?.group(1)?.trim() ?? ''}, original: raw);
    }
    final openMatch = RegExp(r'(?:open|launch|start)\s+(.+)').firstMatch(text);
    if (openMatch != null) {
      return RoutedIntent(intent: SaphiraIntent.openApp, slots: {'app': openMatch.group(1)!.trim()}, original: raw);
    }
    if (text.startsWith('navigate') || text.startsWith('directions') || text.contains('take me to')) {
      final dest = text.replaceFirst(RegExp(r'(navigate(?:\s+to)?|directions(?:\s+to)?|take me to)\s*'), '').trim();
      return RoutedIntent(intent: SaphiraIntent.navigation, slots: {'destination': dest}, original: raw);
    }
    if (text.contains('flashlight') || text.contains('torch')) {
      return RoutedIntent(intent: SaphiraIntent.flashlight, slots: {}, original: raw);
    }
    if (text.contains('wifi') || text.contains('wi-fi')) {
      return RoutedIntent(intent: SaphiraIntent.wifi, slots: {}, original: raw);
    }
    if (text.contains('bluetooth')) {
      return RoutedIntent(intent: SaphiraIntent.bluetooth, slots: {}, original: raw);
    }
    if (RegExp(r'\b(volume|mute|unmute)\b').hasMatch(text)) {
      return RoutedIntent(intent: SaphiraIntent.volume, slots: {'query': text}, original: raw);
    }
    if (text.contains('settings')) {
      return RoutedIntent(intent: SaphiraIntent.settings, slots: {}, original: raw);
    }
    if (text.startsWith('search ') || text.startsWith('google ')) {
      final q = text.replaceFirst(RegExp(r'^(search|google)\s+'), '');
      return RoutedIntent(intent: SaphiraIntent.search, slots: {'query': q}, original: raw);
    }
    return RoutedIntent(intent: SaphiraIntent.chat, slots: {}, original: raw);
  }

  Future<String?> execute(RoutedIntent routed) async {
    final agent = AndroidActionAgent.instance;
    switch (routed.intent) {
      case SaphiraIntent.call: return agent.dial(routed.slots['contact'] ?? '');
      case SaphiraIntent.sms: return agent.sms(routed.slots['contact'] ?? '', body: routed.slots['body']);
      case SaphiraIntent.alarm: return agent.setAlarm(routed.slots['time'] ?? '');
      case SaphiraIntent.openApp: return agent.openApp(routed.slots['app'] ?? '');
      case SaphiraIntent.navigation: return agent.navigate(routed.slots['destination'] ?? '');
      case SaphiraIntent.flashlight: return agent.toggleFlashlight();
      case SaphiraIntent.wifi: return agent.openWifiSettings();
      case SaphiraIntent.bluetooth: return agent.openBluetoothSettings();
      case SaphiraIntent.volume: return agent.openVolumeSettings();
      case SaphiraIntent.settings: return agent.openSettings();
      case SaphiraIntent.search: return agent.webSearch(routed.slots['query'] ?? '');
      default: return null;
    }
  }
}
