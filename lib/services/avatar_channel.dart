// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Client bridge to Saphira /avatar FastAPI endpoints.

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../ui/saphira_avatar_view.dart';

class AvatarChannel {
  final String baseUrl;

  AvatarChannel({this.baseUrl = 'http://localhost:8000'});

  Future<Map<String, dynamic>> status() async {
    final res = await http.get(Uri.parse('$baseUrl/avatar/status'));
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> frame({
    SaphiraAvatarState state = SaphiraAvatarState.idle,
    String extraAction = '',
    String? referenceUrl,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/avatar/frame'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'state': state.name,
        'extra_action': extraAction,
        if (referenceUrl != null) 'reference_url': referenceUrl,
      }),
    );
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> clip({
    SaphiraAvatarState state = SaphiraAvatarState.talking,
    String extraAction = '',
    int durationSec = 4,
    String? referenceUrl,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/avatar/clip'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'state': state.name,
        'extra_action': extraAction,
        'duration_sec': durationSec,
        if (referenceUrl != null) 'reference_url': referenceUrl,
      }),
    );
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> setReference(String url) async {
    final res = await http.post(
      Uri.parse('$baseUrl/avatar/reference'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'url': url}),
    );
    return jsonDecode(res.body) as Map<String, dynamic>;
  }
}
