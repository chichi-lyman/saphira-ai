// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

/// Bidirectional WebSocket client for Saphira real-time voice + chat streaming.
///
/// Connects to the FastAPI orchestrator endpoint:
///   wss://<host>/v1/saphira/stream  (or /api/device/ws depending on deployment)
///
/// Protocol (JSON frames):
///   Client → Server:
///     { "type": "text", "content": "..." }
///     { "type": "audio", "format": "pcm16", "data": "<base64>" }
///     { "type": "ping" }
///   Server → Client:
///     { "type": "transcript", "role": "user|assistant", "content": "..." }
///     { "type": "audio", "format": "mp3|pcm16", "data": "<base64>" }
///     { "type": "tool_call", "server": "...", "tool": "...", "arguments": {} }
///     { "type": "status", "state": "listening|thinking|speaking|idle" }
///     { "type": "error", "message": "..." }
class SaphiraWebSocketVoiceClient extends ChangeNotifier {
  SaphiraWebSocketVoiceClient({
    required this.baseUrl,
    this.authToken,
    this.deviceId,
  });

  /// e.g. "wss://api.saphira.example" or "ws://10.0.2.2:8000" for emulator
  final String baseUrl;
  final String? authToken;
  final String? deviceId;

  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _pingTimer;
  bool _connected = false;
  String _connectionState = 'idle'; // idle | connecting | connected | reconnecting | error
  String? _lastError;

  final _transcriptController = StreamController<TranscriptEvent>.broadcast();
  final _audioController = StreamController<AudioEvent>.broadcast();
  final _statusController = StreamController<String>.broadcast();
  final _toolCallController = StreamController<ToolCallEvent>.broadcast();

  Stream<TranscriptEvent> get transcripts => _transcriptController.stream;
  Stream<AudioEvent> get audioChunks => _audioController.stream;
  Stream<String> get statusStream => _statusController.stream;
  Stream<ToolCallEvent> get toolCalls => _toolCallController.stream;

  bool get isConnected => _connected;
  String get connectionState => _connectionState;
  String? get lastError => _lastError;

  /// Open the WebSocket and start the keep-alive ping loop.
  Future<void> connect() async {
    if (_connected) return;

    _setState('connecting');
    final uri = _buildUri();

    try {
      _channel = WebSocketChannel.connect(uri);
      await _channel!.ready;

      _subscription = _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
        cancelOnError: false,
      );

      _connected = true;
      _setState('connected');
      _startPing();

      // Announce device identity
      sendJson({
        'type': 'hello',
        'device_id': deviceId ?? 'flutter-client',
        'client': 'saphira_flutter',
        'version': '1.0.0',
      });
    } catch (e) {
      _lastError = e.toString();
      _setState('error');
      rethrow;
    }
  }

  Uri _buildUri() {
    final normalized = baseUrl.replaceAll(RegExp(r'/$'), '');
    // Prefer dedicated stream path; fall back to device WS if configured that way
    var path = '/v1/saphira/stream';
    if (normalized.contains('/api')) {
      path = '/api/device/ws';
    }
    final wsBase = normalized
        .replaceFirst('https://', 'wss://')
        .replaceFirst('http://', 'ws://');
    final uri = Uri.parse('$wsBase$path');
    final params = <String, String>{};
    if (authToken != null && authToken!.isNotEmpty) {
      params['token'] = authToken!;
    }
    if (deviceId != null) params['device_id'] = deviceId!;
    return uri.replace(queryParameters: params.isEmpty ? null : params);
  }

  void _onMessage(dynamic raw) {
    try {
      final Map<String, dynamic> msg =
          raw is String ? jsonDecode(raw) as Map<String, dynamic> : raw as Map<String, dynamic>;

      final type = msg['type'] as String? ?? '';

      switch (type) {
        case 'transcript':
          _transcriptController.add(TranscriptEvent(
            role: msg['role'] as String? ?? 'assistant',
            content: msg['content'] as String? ?? '',
            isFinal: msg['final'] as bool? ?? true,
          ));
          break;
        case 'audio':
          _audioController.add(AudioEvent(
            format: msg['format'] as String? ?? 'pcm16',
            base64Data: msg['data'] as String? ?? '',
          ));
          break;
        case 'status':
          final state = msg['state'] as String? ?? 'idle';
          _statusController.add(state);
          break;
        case 'tool_call':
          _toolCallController.add(ToolCallEvent(
            server: msg['server'] as String? ?? '',
            tool: msg['tool'] as String? ?? '',
            arguments: Map<String, dynamic>.from(msg['arguments'] as Map? ?? {}),
          ));
          break;
        case 'error':
          _lastError = msg['message'] as String? ?? 'unknown error';
          notifyListeners();
          break;
        case 'pong':
          // keep-alive ack
          break;
        default:
          debugPrint('[SaphiraWS] unhandled frame type: $type');
      }
    } catch (e) {
      debugPrint('[SaphiraWS] parse error: $e');
    }
  }

  void _onError(Object error) {
    _lastError = error.toString();
    _connected = false;
    _setState('error');
    _scheduleReconnect();
  }

  void _onDone() {
    _connected = false;
    _setState('idle');
    _scheduleReconnect();
  }

  void _scheduleReconnect() {
    if (_connectionState == 'reconnecting') return;
    _setState('reconnecting');
    Future.delayed(const Duration(seconds: 3), () {
      if (!_connected) connect().catchError((_) {});
    });
  }

  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 25), (_) {
      if (_connected) sendJson({'type': 'ping'});
    });
  }

  void _setState(String s) {
    _connectionState = s;
    notifyListeners();
  }

  // ── Outbound helpers ──────────────────────────────────────────────────────

  void sendJson(Map<String, dynamic> payload) {
    if (_channel == null || !_connected) return;
    _channel!.sink.add(jsonEncode(payload));
  }

  /// Send a plain text utterance (typed or STT result).
  void sendText(String content) {
    sendJson({'type': 'text', 'content': content});
  }

  /// Stream a base64-encoded PCM16 / Opus audio chunk.
  void sendAudioChunk({required String base64Data, String format = 'pcm16'}) {
    sendJson({'type': 'audio', 'format': format, 'data': base64Data});
  }

  /// Signal end-of-utterance so the backend can finalize STT + respond.
  void endUtterance() {
    sendJson({'type': 'end_of_utterance'});
  }

  Future<void> disconnect() async {
    _pingTimer?.cancel();
    await _subscription?.cancel();
    await _channel?.sink.close(status.normalClosure);
    _channel = null;
    _connected = false;
    _setState('idle');
  }

  @override
  void dispose() {
    disconnect();
    _transcriptController.close();
    _audioController.close();
    _statusController.close();
    _toolCallController.close();
    super.dispose();
  }
}

// ── Event models ────────────────────────────────────────────────────────────

class TranscriptEvent {
  final String role;
  final String content;
  final bool isFinal;
  TranscriptEvent({required this.role, required this.content, this.isFinal = true});
}

class AudioEvent {
  final String format;
  final String base64Data;
  AudioEvent({required this.format, required this.base64Data});
}

class ToolCallEvent {
  final String server;
  final String tool;
  final Map<String, dynamic> arguments;
  ToolCallEvent({required this.server, required this.tool, required this.arguments});
}
