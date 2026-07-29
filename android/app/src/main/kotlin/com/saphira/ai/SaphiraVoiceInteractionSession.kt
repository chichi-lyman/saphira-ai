// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// One assistant invocation session — shows UI / notifies Flutter to open overlay.
// L1 actions must still pass AutonomyGate + user confirm in Flutter.

package com.saphira.ai

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.voice.VoiceInteractionSession
import android.util.Log

class SaphiraVoiceInteractionSession(context: Context) : VoiceInteractionSession(context) {

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "Session created")
    }

    override fun onShow(args: Bundle?, showFlags: Int) {
        super.onShow(args, showFlags)
        Log.i(TAG, "Session show flags=$showFlags")
        // Bring Saphira UI forward (MainActivity hosts Flutter overlay)
        val launch = Intent(context, MainActivity::class.java).apply {
            action = SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP)
            putExtra("source", "voice_interaction")
            putExtra("show_overlay", true)
        }
        try {
            context.startActivity(launch)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to launch MainActivity for assistant session", e)
        }
    }

    override fun onHide() {
        Log.i(TAG, "Session hide")
        super.onHide()
    }

    companion object {
        private const val TAG = "SaphiraVISSession"
    }
}
