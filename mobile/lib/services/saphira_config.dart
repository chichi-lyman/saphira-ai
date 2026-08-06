// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SaphiraConfig extends ChangeNotifier {
  static const _keyApiBase = 'saphira_api_base';
  static const _defaultApi = 'https://your-saphira-backend.example.com';

  String _apiBaseUrl = _defaultApi;

  String get apiBaseUrl => _apiBaseUrl;

  static Future<SaphiraConfig> load() async {
    final prefs = await SharedPreferences.getInstance();
    final config = SaphiraConfig();
    config._apiBaseUrl = prefs.getString(_keyApiBase) ?? _defaultApi;
    return config;
  }

  Future<void> setApiBaseUrl(String url) async {
    _apiBaseUrl = url.trim().replaceAll(RegExp(r'/$'), '');
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyApiBase, _apiBaseUrl);
    notifyListeners();
  }
}
