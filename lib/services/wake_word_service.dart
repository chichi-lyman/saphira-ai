// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// "Hey Saphira" / "Okay Saphira" via Porcupine — opens overlay only (no L1 auto-run)

import 'package:flutter/foundation.dart';

typedef OnWakeWord = void Function();

class WakeWordService {
  OnWakeWord? onDetected;
  bool _running = false;
  // PorcupineManager? _porcupineManager;

  bool get isRunning => _running;

  /// accessKey from Picovoice console; keyword asset trained as Hey Saphira / Okay Saphira.
  Future<void> initWakeWord(
    OnWakeWord onWakeWordDetected, {
    String? accessKey,
    String keywordAsset = 'assets/wake_words/Hey-Saphira_en_android.ppn',
  }) async {
    onDetected = onWakeWordDetected;
    // Production:
    // import 'package:porcupine_flutter/porcupine_manager.dart';
    // _porcupineManager = await PorcupineManager.fromKeywordPaths(
    //   accessKey ?? const String.fromEnvironment('PICOVOICE_ACCESS_KEY'),
    //   [keywordAsset],
    //   (int keywordIndex) {
    //     if (keywordIndex == 0) onDetected?.call();
    //   },
    // );
    // await _porcupineManager?.start();
    _running = true;
    debugPrint(
      'WakeWordService ready (wire Porcupine + $keywordAsset for device)',
    );
  }

  Future<void> start() async {
    _running = true;
    // await _porcupineManager?.start();
  }

  Future<void> stop() async {
    _running = false;
    // await _porcupineManager?.stop();
  }

  void simulateWakeWord() => onDetected?.call();
}
