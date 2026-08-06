// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// TTS helper — prefers backend ElevenLabs proxy (returns audio/mpeg).
// Falls back to device flutter_tts when backend is unavailable.

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:just_audio/just_audio.dart';

class SaphiraTts {
  final String? backendTtsUrl;
  final FlutterTts _deviceTts = FlutterTts();
  final AudioPlayer _player = AudioPlayer();
  bool _deviceReady = false;

  SaphiraTts({this.backendTtsUrl}) {
    _initDevice();
  }

  Future<void> _initDevice() async {
    try {
      await _deviceTts.setLanguage('en-US');
      await _deviceTts.setSpeechRate(0.48);
      await _deviceTts.setPitch(1.05);
      _deviceReady = true;
    } catch (e) {
      debugPrint('Device TTS init failed: $e');
    }
  }

  Future<void> speak(String text, {String style = 'assist'}) async {
    if (text.trim().isEmpty) return;

    if (backendTtsUrl != null && backendTtsUrl!.isNotEmpty) {
      final ok = await _playFromBackend(text, style);
      if (ok) return;
    }

    if (_deviceReady) {
      await _deviceTts.speak(text);
    }
  }

  Future<bool> _playFromBackend(String text, String style) async {
    try {
      final res = await http.post(
        Uri.parse(backendTtsUrl!),
        headers: {'Content-Type': 'application/json'},
        body: '{"text":${_jsonString(text)},"style":"$style","product":"Saphira"}',
      ).timeout(const Duration(seconds: 25));

      if (res.statusCode != 200 || res.bodyBytes.isEmpty) {
        debugPrint('Backend TTS HTTP ${res.statusCode}');
        return false;
      }

      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/saphira_tts_${DateTime.now().millisecondsSinceEpoch}.mp3');
      await file.writeAsBytes(res.bodyBytes, flush: true);

      await _player.stop();
      await _player.setFilePath(file.path);
      await _player.play();

      _player.playerStateStream.listen((state) {
        if (state.processingState == ProcessingState.completed) {
          try { file.deleteSync(); } catch (_) {}
        }
      });

      return true;
    } catch (e) {
      debugPrint('Backend TTS play failed: $e');
      return false;
    }
  }

  String _jsonString(String s) {
    return '"${s.replaceAll(r'\', r'\\').replaceAll('"', r'\"').replaceAll('\n', r'\n')}"';
  }

  Future<void> stop() async {
    await _player.stop();
    await _deviceTts.stop();
  }

  void dispose() {
    _player.dispose();
  }
}
