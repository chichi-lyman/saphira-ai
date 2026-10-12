// Copyright © 2026 Chelsea Megan Woods
// Saphira AI — Flutter mobile client with floating overlay drawer

import 'package:flutter/material.dart';
import 'package:flutter_overlay_window/flutter_overlay_window.dart';

void main() {
  runApp(const SaphiraApp());
}

class SaphiraApp extends StatelessWidget {
  const SaphiraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Saphira AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        colorScheme: ColorScheme.dark(
          primary: Colors.cyanAccent,
          secondary: Colors.blueAccent,
        ),
      ),
      home: const SaphiraHome(),
    );
  }
}

class SaphiraHome extends StatefulWidget {
  const SaphiraHome({super.key});

  @override
  State<SaphiraHome> createState() => _SaphiraHomeState();
}

class _SaphiraHomeState extends State<SaphiraHome> {
  bool _opening = false;

  Future<void> _openOverlay() async {
    if (_opening) return;
    setState(() => _opening = true);

    try {
      final allowed = await FlutterOverlayWindow.isPermissionGranted();

      if (!allowed) {
        final granted = await FlutterOverlayWindow.requestPermission();
        if (granted != true || !mounted) return;
      }

      await FlutterOverlayWindow.showOverlay(
        height: 520,
        width: 340,
        alignment: OverlayAlignment.centerRight,
        enableDrag: true,
        overlayTitle: 'Saphira AI',
        overlayContent: 'Personal assistant',
      );
    } finally {
      if (mounted) setState(() => _opening = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Saphira AI')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'Unified Personal AI Operating System',
              style: TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _opening ? null : _openOverlay,
              icon: const Icon(Icons.open_in_new),
              label: const Text('Open floating assistant'),
            ),
          ],
        ),
      ),
    );
  }
}
