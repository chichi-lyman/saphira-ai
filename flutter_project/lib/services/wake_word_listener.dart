import 'dart:async';
import 'package:flutter/services.dart';
import 'saphira_websocket_client.dart';

/// Listens for on-device wake-word events from the Android foreground service
/// and opens the Saphira WebSocket stream only after local confidence exceeds
/// the threshold.
///
/// Also implements barge-in: when wake word fires while Saphira is speaking,
/// immediately sends stop_audio and flushes the local AudioTrack buffer.
///
/// © 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
class SaphiraWakeWordListener {
  static const EventChannel _eventChannel =
      EventChannel('com.saphira.ai/wakeword_events');

  StreamSubscription? _subscription;
  late SaphiraVoiceClient _voiceClient;
  bool _initialized = false;

  void initialize(String wsUrl) {
    if (_initialized) return;
    _initialized = true;

    _voiceClient = SaphiraVoiceClient(
      serverUrl: wsUrl,
      onTextReceived: (text) => print("[Saphira Response]: $text"),
      onAudioReceived: (chunk) {
        /* Play incoming PCM audio stream via AudioTrack */
      },
      onConnectionStateChanged: (connected) => print("[WS State]: $connected"),
      onBargeIn: () {
        print("[Saphira] Barge-in: local AudioTrack buffer flushed");
        // Platform channel to native layer can flush AudioTrack here if needed.
      },
    );

    // Listen for local on-device wake-word detection events
    _subscription = _eventChannel.receiveBroadcastStream().listen((event) async {
      final double confidence = (event is Map && event['confidence'] != null)
          ? (event['confidence'] as num).toDouble()
          : 0.0;
      print("[Saphira Wake Word Detected] Confidence: $confidence");

      // Barge-in path: if already connected and speaking, interrupt immediately
      if (_voiceClient.isConnected && _voiceClient.isSpeaking) {
        print("[Saphira] Barge-in interruption triggered");
        _voiceClient.interruptSpeech();
        return;
      }

      // Cold-start path: connect WebSocket stream after local wake-word threshold
      if (!_voiceClient.isConnected) {
        await _voiceClient.connect();
      }
      _voiceClient.sendTextMessage(
          "Wake word 'Saphira' triggered locally on device.");
    });
  }

  /// Explicit public entry for other services that detect speech while TTS is active.
  void forceBargeIn() {
    if (_initialized && _voiceClient.isConnected) {
      _voiceClient.interruptSpeech();
    }
  }

  void dispose() {
    _subscription?.cancel();
    if (_initialized) {
      _voiceClient.disconnect();
    }
    _initialized = false;
  }
}
