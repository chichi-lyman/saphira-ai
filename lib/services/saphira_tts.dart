// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Saphira TTS — plays Chelsea-cloned voice via backend or ElevenLabs proxy

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class SaphiraTts {
  /// Backend endpoint that holds ELEVENLABS_API_KEY server-side (preferred).
  final String? backendTtsUrl;

  SaphiraTts({this.backendTtsUrl});

  /// Request speech audio for [text].
  /// style: assist | social | confirm_l1
  Future<Uri?> speakUrl(String text, {String style = 'assist'}) async {
    final base = backendTtsUrl;
    if (base == null || base.isEmpty) {
      debugPrint('SaphiraTts: no backendTtsUrl — configure voice proxy');
      return null;
    }
    final res = await http.post(
      Uri.parse(base),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'style': style,
        'product': 'Saphira',
        'owner': 'Chelsea Megan Woods',
      }),
    );
    if (res.statusCode >= 200 && res.statusCode < 300) {
      final data = jsonDecode(res.body);
      final url = data['audio_url'] as String?;
      if (url != null) return Uri.parse(url);
    }
    debugPrint('SaphiraTts failed: ${res.statusCode}');
    return null;
  }
}
