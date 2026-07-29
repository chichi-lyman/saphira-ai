// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Wake word: "Hey Saphira" / "Okay Saphira" via Porcupine (Picovoice)
// Requires: porcupine_flutter + custom .ppn asset + Picovoice access key

import 'package:flutter/foundation.dart';

/// Callback when wake word is detected — should open overlay (not auto L1 actions).
typedef OnWakeWord = void Function();

class WakeWordService {
  OnWakeWord? onDetected;
  bool _running = false;

  bool get isRunning => _running;

  /// Initialize keyword engine.
  /// Replace stub with PorcupineManager.fromKeywordPaths when key + assets exist.
  Future<void> initWakeWord(OnWakeWord onWakeWordDetected) async {
    onDetected = onWakeWordDetected;
    // Production:
    // _porcupineManager = await PorcupineManager.fromKeywordPaths(
    //   accessKey,
    //   ['assets/wake_words/Hey-Saphira_en_android.ppn'],
    //   (int keywordIndex) { if (keywordIndex == 0) onDetected?.call(); },
    // );
    // await _porcupineManager?.start();
    _running = true;
    debugPrint('Saphira WakeWordService: initialized (wire Porcupine for production)');
  }

  Future<void> start() async {
    _running = true;
  }

  Future<void> stop() async {
    _running = false;
    // await _porcupineManager?.stop();
  }

  /// Test hook for simulator / debug without mic model.
  void simulateWakeWord() {
    onDetected?.call();
  }
}
