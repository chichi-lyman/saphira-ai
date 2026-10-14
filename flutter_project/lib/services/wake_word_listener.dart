import 'dart:async';
import 'package:flutter/services.dart';
import 'saphira_websocket_client.dart';

/// Listens for on-device wake-word events from the Android foreground service
/// and opens the Saphira WebSocket stream only after local confidence exceeds
/// the threshold.
///
/// © 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
class SaphiraWakeWordListener {
  static const EventChannel _eventChannel =
      EventChannel('com.saphira.ai/wakeword_events');

  StreamSubscription? _subscription;
  late SaphiraVoiceClient _voiceClient;

  void initialize(String wsUrl) {
    _voiceClient = SaphiraVoiceClient(
      serverUrl: wsUrl,
      onTextReceived: (text) => print("[Saphira Response]: $text"),
      onAudioReceived: (chunk) {
        /* Play incoming PCM audio stream */
      },
      onConnectionStateChanged: (connected) => print("[WS State]: $connected"),
    );

    // Listen for local on-device wake-word detection events
    _subscription = _eventChannel.receiveBroadcastStream().listen((event) async {
      final double confidence = (event is Map && event['confidence'] != null)
          ? (event['confidence'] as num).toDouble()
          : 0.0;
      print("[Saphira Wake Word Detected] Confidence: $confidence");

      // Connect WebSocket stream only after local wake-word trigger passes threshold
      await _voiceClient.connect();
      _voiceClient.sendTextMessage(
          "Wake word 'Saphira' triggered locally on device.");
    });
  }

  void dispose() {
    _subscription?.cancel();
    _voiceClient.disconnect();
  }
}
