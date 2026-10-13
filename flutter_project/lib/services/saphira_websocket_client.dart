// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella
//
// lib/services/saphira_websocket_client.dart
// Dual WebSocket stream for low-latency voice/text transport to the
// Saphira FastAPI orchestrator.

import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as ws_status;

class SaphiraVoiceClient {
  WebSocketChannel? _channel;
  final String serverUrl;
  final void Function(String text) onTextReceived;
  final void Function(Uint8List audioChunk) onAudioReceived;
  final void Function(bool isConnected) onConnectionStateChanged;

  bool _isConnected = false;
  Timer? _pingTimer;

  SaphiraVoiceClient({
    required this.serverUrl,
    required this.onTextReceived,
    required this.onAudioReceived,
    required this.onConnectionStateChanged,
  });

  bool get isConnected => _isConnected;

  /// Establishes dual WebSocket stream for low-latency voice/text transport.
  Future<void> connect() async {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(serverUrl));
      await _channel!.ready;

      _isConnected = true;
      onConnectionStateChanged(true);

      _channel!.stream.listen(
        (data) {
          if (data is String) {
            try {
              final parsed = jsonDecode(data) as Map<String, dynamic>;
              final type = parsed['type'] as String? ?? '';
              if (type == 'text_delta' || type == 'transcript' || type == 'text') {
                onTextReceived(parsed['content'] as String? ?? '');
              }
            } catch (_) {
              // plain text frame
              onTextReceived(data);
            }
          } else if (data is Uint8List) {
            onAudioReceived(data);
          } else if (data is List<int>) {
            onAudioReceived(Uint8List.fromList(data));
          }
        },
        onError: (_) => _handleDisconnect(),
        onDone: () => _handleDisconnect(),
        cancelOnError: false,
      );

      _startPing();
    } catch (e) {
      _handleDisconnect();
      rethrow;
    }
  }

  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 25), (_) {
      if (_isConnected && _channel != null) {
        _channel!.sink.add(jsonEncode({'type': 'ping'}));
      }
    });
  }

  /// Sends raw PCM audio chunks captured from device microphone.
  void sendAudioChunk(Uint8List audioChunk) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(audioChunk);
    }
  }

  /// Transmits immediate text payloads or agent command triggers.
  void sendTextMessage(String message) {
    if (_isConnected && _channel != null) {
      final payload = jsonEncode({
        'type': 'user_text',
        'content': message,
        'timestamp': DateTime.now().toIso8601String(),
      });
      _channel!.sink.add(payload);
    }
  }

  void _handleDisconnect() {
    _pingTimer?.cancel();
    _isConnected = false;
    onConnectionStateChanged(false);
  }

  void disconnect() {
    _pingTimer?.cancel();
    _channel?.sink.close(ws_status.normalClosure);
    _channel = null;
    _handleDisconnect();
  }
}
