// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Host activity for Flutter. Handles assistant-invoked intents and
// registers MethodChannels for accessibility + assistant overlay.

package com.saphira.ai

import android.content.Intent
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {

    private var assistantChannel: MethodChannel? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        // Assistant overlay channel
        assistantChannel = MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            ASSISTANT_CHANNEL
        )
        handleAssistantIntent(intent)

        // Accessibility bridge channel
        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            A11Y_CHANNEL
        ).setMethodCallHandler { call, result ->
            val svc = SaphiraAccessibilityService.instance
            if (svc == null && call.method != "isAvailable") {
                result.error("UNAVAILABLE", "Accessibility service not enabled", null)
                return@setMethodCallHandler
            }
            try {
                when (call.method) {
                    "isAvailable" -> result.success(svc != null)
                    "authorize" -> {
                        val token = call.argument<String>("token") ?: ""
                        val ttl = call.argument<Number>("ttlMs")?.toLong() ?: 30_000L
                        result.success(svc!!.authorize(token, ttl))
                    }
                    "revokeAuth" -> {
                        svc!!.revokeAuth()
                        result.success(null)
                    }
                    "clickElementByText" -> {
                        val text = call.argument<String>("text") ?: ""
                        result.success(svc!!.clickElementByText(text))
                    }
                    "injectText" -> {
                        val text = call.argument<String>("text") ?: ""
                        result.success(svc!!.injectTextIntoFocusedInput(text))
                    }
                    "tapAt" -> {
                        val x = call.argument<Double>("x")?.toFloat() ?: 0f
                        val y = call.argument<Double>("y")?.toFloat() ?: 0f
                        result.success(svc!!.performTapAtCoordinates(x, y))
                    }
                    "globalAction" -> {
                        val name = call.argument<String>("name") ?: ""
                        result.success(svc!!.globalAction(name))
                    }
                    else -> result.notImplemented()
                }
            } catch (e: Exception) {
                Log.e(TAG, "A11y method ${call.method} failed", e)
                result.error("ERROR", e.message, null)
            }
        }
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
            Log.i(TAG, "Assistant invoked — requesting Flutter overlay")
            assistantChannel?.invokeMethod(
                "openOverlay",
                mapOf(
                    "source" to (intent.getStringExtra("source") ?: "voice_interaction"),
                    "show_overlay" to true
                )
            )
        }
    }

    companion object {
        private const val TAG = "SaphiraMain"
        const val ASSISTANT_CHANNEL = "com.saphira.ai/assistant"
        const val A11Y_CHANNEL = "com.saphira.ai/accessibility"
    }
}
