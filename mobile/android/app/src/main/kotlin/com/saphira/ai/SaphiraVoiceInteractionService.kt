// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// System VoiceInteractionService entry point. Android starts this when the user
// long-presses home/power or otherwise invokes the default device assistant.

package com.saphira.ai

import android.service.voice.VoiceInteractionService
import android.util.Log

class SaphiraVoiceInteractionService : VoiceInteractionService() {

    override fun onReady() {
        super.onReady()
        Log.i(TAG, "Saphira VoiceInteractionService ready — eligible for ROLE_ASSISTANT")
    }

    override fun onShutdown() {
        Log.i(TAG, "Saphira VoiceInteractionService shutting down")
        super.onShutdown()
    }

    companion object {
        private const val TAG = "SaphiraVIS"
        /** Custom action used when the session launches MainActivity. */
        const val ACTION_ASSISTANT_INVOKED = "com.saphira.ai.ACTION_ASSISTANT_INVOKED"
    }
}
