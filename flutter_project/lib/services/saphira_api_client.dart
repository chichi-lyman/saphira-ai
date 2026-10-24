// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Nova Umbrella

import 'dart:convert';

import 'package:http/http.dart' as http;

/// Thin REST client for Saphira FastAPI endpoints that are not streamed.
/// Primary use: dispatch MCP tool calls and fetch tool catalog.
class SaphiraApiClient {
  SaphiraApiClient({
    required this.baseUrl,
    this.authToken,
  });

  /// e.g. "https://api.saphira.example" (no trailing slash)
  final String baseUrl;
  final String? authToken;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (authToken != null && authToken!.isNotEmpty)
          'Authorization': 'Bearer $authToken',
      };

  Uri _uri(String path) {
    final normalized = baseUrl.replaceAll(RegExp(r'/$'), '');
    return Uri.parse('$normalized$path');
  }

  /// GET /api/mcp/tools
  Future<Map<String, dynamic>> listMcpTools() async {
    final res = await http.get(_uri('/api/mcp/tools'), headers: _headers);
    if (res.statusCode != 200) {
      throw Exception('listMcpTools failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  /// POST /api/mcp/execute
  Future<Map<String, dynamic>> executeMcpTool({
    required String serverName,
    required String toolName,
    Map<String, dynamic> arguments = const {},
  }) async {
    final body = jsonEncode({
      'server_name': serverName,
      'tool_name': toolName,
      'arguments': arguments,
    });
    final res = await http.post(
      _uri('/api/mcp/execute'),
      headers: _headers,
      body: body,
    );
    if (res.statusCode != 200) {
      throw Exception('executeMcpTool failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  /// POST /api/mcp/connect – register a new MCP server at runtime
  Future<Map<String, dynamic>> connectMcpServer({
    required String serverName,
    required String command,
    List<String> args = const [],
    Map<String, String>? env,
  }) async {
    final body = jsonEncode({
      'server_name': serverName,
      'command': command,
      'args': args,
      if (env != null) 'env': env,
    });
    final res = await http.post(
      _uri('/api/mcp/connect'),
      headers: _headers,
      body: body,
    );
    if (res.statusCode != 200) {
      throw Exception('connectMcpServer failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  /// Simple health probe
  Future<bool> healthCheck() async {
    try {
      final res = await http.get(_uri('/health'), headers: _headers);
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
