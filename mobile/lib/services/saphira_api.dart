// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class SaphiraApi {
  final String baseUrl;

  SaphiraApi({required this.baseUrl});

  Uri _u(String path) => Uri.parse('$baseUrl$path');

  Future<Map<String, dynamic>> chat({
    required String message,
    bool confirmed = false,
    String? sessionId,
    String? room,
  }) async {
    try {
      final res = await http.post(
        _u('/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'message': message,
          'confirmed': confirmed,
          if (sessionId != null) 'session_id': sessionId,
          if (room != null) 'room': room,
        }),
      ).timeout(const Duration(seconds: 45));

      if (res.statusCode >= 200 && res.statusCode < 300) {
        return jsonDecode(res.body) as Map<String, dynamic>;
      }
      return {
        'message': "I'm having a moment — please try again shortly.",
        'avatar_state': 'thinking',
        'status': 'error',
      };
    } catch (e) {
      debugPrint('SaphiraApi chat exception: $e');
      return {
        'message': "I can't reach the servers right now. Check your connection.",
        'avatar_state': 'thinking',
        'status': 'offline',
      };
    }
  }

  Future<bool> isOnline() async {
    try {
      final res = await http.get(_u('/')).timeout(const Duration(seconds: 8));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
