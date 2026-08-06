// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Host activity for Flutter. Bidirectional MethodChannel bridge for
// VoiceInteractionService \u2194 Flutter communication.

package com.saphira.ai

import android.content.Intent
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {

    private var methodChannel: MethodChannel? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        methodChannel = MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            CHANNEL
        ).also { channel ->
            channel.setMethodCallHandler { call, result ->
                when (call.method) {
                    "startListening" -> {
                        Log.i(TAG, "Flutter requested startListening")
                        result.success(true)
                    }
                    "stopListening" -> {
                        Log.i(TAG, "Flutter requested stopListening")
                        result.success(true)
                    }
                    "overlayReady" -> {
                        Log.i(TAG, "Flutter overlay is ready")
                        result.success(null)
                    }
                    "endSession" -> {
                        Log.i(TAG, "Flutter requested endSession")
                        result.success(null)
                    }
                    else -> result.notImplemented()
                }
            }
        }

        handleAssistantIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAssistantIntent(intent)
    }

    private fun handleAssistantIntent(intent: Intent?) {
        if (intent == null) return

        val fromAssistant =
            intent.action == SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED ||
                intent.getBooleanExtra("show_overlay", false)

        if (fromAssistant) {
            val source = intent.getStringExtra("source") ?: "voice_interaction"
            Log.i(TAG, "Assistant invoked \u2014 source=$source")

            methodChannel?.invokeMethod(
                "openOverlay",
                mapOf(
                    "source" to source,
                    "show_overlay" to true
                )
            )
        }
    }

    companion object {
        private const val TAG = "SaphiraMain"
        const val CHANNEL = "com.saphira.ai/assistant"
    }
}
