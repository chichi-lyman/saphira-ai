// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Flutter Voice Service Bridge
// Handles communication with native Android voice service

import 'package:flutter/services.dart';
import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';

class VoiceServiceBridge {
  static const platform = MethodChannel('com.saphira/voice_service');
  static const platform_events = EventChannel('com.saphira/voice_events');
  
  static final VoiceServiceBridge _instance = VoiceServiceBridge._internal();
  
  bool _isServiceReady = false;
  StreamSubscription? _eventSubscription;
  
  // Callbacks for voice events
  Function(String)? onVoiceInput;
  Function(String)? onError;
  Function()? onServiceReady;
  
  VoiceServiceBridge._internal();
  
  factory VoiceServiceBridge() {
    return _instance;
  }
  
  Future<void> initialize() async {
    try {
      final result = await platform.invokeMethod('initialize');
      _isServiceReady = true;
      onServiceReady?.call();
      debugPrint('Voice service initialized: $result');
      _listenToVoiceEvents();
    } on PlatformException catch (e) {
      debugPrint('Error initializing voice service: ${e.message}');
      onError?.call('Failed to initialize: ${e.message}');
      // Fall back to text mode
      _isServiceReady = false;
    } catch (e) {
      debugPrint('Unexpected error initializing voice service: $e');
      onError?.call('Unexpected error: $e');
      _isServiceReady = false;
    }
  }
  
  Future<bool> sendAudioToVoiceService(
    Uint8List audioBytes, {
    String format = 'pcm',
    int sampleRate = 16000,
  }) async {
    if (!_isServiceReady) {
      debugPrint('Voice service not ready, skipping audio send');
      return false;
    }
    
    try {
      final result = await platform.invokeMethod('processAudio', {
        'audio': audioBytes,
        'format': format,
        'sampleRate': sampleRate,
      }).timeout(
        const Duration(seconds: 5),
        onTimeout: () => throw TimeoutException('Audio processing timeout'),
      );
      
      debugPrint('Audio sent to voice service: $result');
      return true;
    } on TimeoutException catch (e) {
      debugPrint('Voice service timeout: ${e.message}');
      onError?.call('Voice service timeout - falling back to text mode');
      // Don't crash - just continue without voice
      return false;
    } on PlatformException catch (e) {
      debugPrint('PlatformException sending audio: ${e.message}');
      onError?.call('Voice service error: ${e.message}');
      // Fall back gracefully
      return false;
    } catch (e) {
      debugPrint('Unexpected error sending audio: $e');
      onError?.call('Unexpected voice error: $e');
      // Silently fall back to text mode
      return false;
    }
  }
  
  Future<bool> startListening() async {
    if (!_isServiceReady) {
      debugPrint('Voice service not ready');
      return false;
    }
    
    try {
      final result = await platform.invokeMethod('startListening');
      debugPrint('Listening started: $result');
      return true;
    } on PlatformException catch (e) {
      debugPrint('Error starting listening: ${e.message}');
      onError?.call('Failed to start listening: ${e.message}');
      return false;
    } catch (e) {
      debugPrint('Unexpected error starting listening: $e');
      return false;
    }
  }
  
  Future<bool> stopListening() async {
    if (!_isServiceReady) {
      return false;
    }
    
    try {
      final result = await platform.invokeMethod('stopListening');
      debugPrint('Listening stopped: $result');
      return true;
    } on PlatformException catch (e) {
      debugPrint('Error stopping listening: ${e.message}');
      return false;
    } catch (e) {
      debugPrint('Unexpected error stopping listening: $e');
      return false;
    }
  }
  
  void _listenToVoiceEvents() {
    try {
      platform_events.receiveBroadcastStream().listen(
        (event) {
          try {
            if (event is Map) {
              final eventType = event['type'];
              final data = event['data'];
              
              if (eventType == 'voice_input') {
                onVoiceInput?.call(data);
              } else if (eventType == 'error') {
                onError?.call(data);
              }
            }
          } catch (e) {
            debugPrint('Error processing voice event: $e');
          }
        },
        onError: (error) {
          debugPrint('Error in voice event stream: $error');
          onError?.call('Voice stream error: $error');
          // Try to reinitialize
          Future.delayed(const Duration(seconds: 2), () {
            initialize();
          });
        },
      );
    } catch (e) {
      debugPrint('Error setting up voice event listener: $e');
    }
  }
  
  Future<void> dispose() async {
    try {
      await _eventSubscription?.cancel();
      await platform.invokeMethod('destroy');
      _isServiceReady = false;
    } catch (e) {
      debugPrint('Error disposing voice service: $e');
    }
  }
  
  bool get isServiceReady => _isServiceReady;
  
  // Fallback to text mode if voice fails
  Future<void> enableTextMode() async {
    debugPrint('Falling back to text mode');
    await dispose();
    // UI will show text input instead of voice
  }
}

class TimeoutException implements Exception {
  final String message;
  TimeoutException(this.message);
  
  @override
  String toString() => 'TimeoutException: $message';
}
