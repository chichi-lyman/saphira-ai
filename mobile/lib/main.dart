// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Saphira AI — main entry point.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:permission_handler/permission_handler.dart';

import 'ui/saphira_chat_screen.dart';
import 'services/saphira_config.dart';
import 'services/saphira_api.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));

  final config = await SaphiraConfig.load();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: config),
        Provider(create: (_) => SaphiraApi(baseUrl: config.apiBaseUrl)),
      ],
      child: const SaphiraApp(),
    ),
  );
}

class SaphiraApp extends StatelessWidget {
  const SaphiraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Saphira AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0A12),
        primaryColor: const Color(0xFF00E5FF),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00E5FF),
          secondary: Color(0xFF9D00FF),
          surface: Color(0xFF12121A),
          background: Color(0xFF0A0A12),
        ),
        fontFamily: 'Roboto',
        useMaterial3: true,
      ),
      home: const PermissionGate(child: SaphiraChatScreen()),
    );
  }
}

class PermissionGate extends StatefulWidget {
  final Widget child;
  const PermissionGate({super.key, required this.child});

  @override
  State<PermissionGate> createState() => _PermissionGateState();
}

class _PermissionGateState extends State<PermissionGate> {
  bool _ready = false;

  @override
  void initState() {
    super.initState();
    _request();
  }

  Future<void> _request() async {
    await [Permission.microphone, Permission.speech].request();
    if (mounted) setState(() => _ready = true);
  }

  @override
  Widget build(BuildContext context) {
    if (!_ready) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: Color(0xFF00E5FF))),
      );
    }
    return widget.child;
  }
}
