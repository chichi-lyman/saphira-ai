// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
package com.saphira.ai

import android.service.voice.VoiceInteractionService
import android.util.Log

class SaphiraVoiceInteractionService : VoiceInteractionService() {
    override fun onReady() {
        super.onReady()
        Log.i(TAG, "Saphira VoiceInteractionService ready")
    }
    companion object {
        private const val TAG = "SaphiraVIS"
        const val ACTION_ASSISTANT_INVOKED = "com.saphira.ai.ACTION_ASSISTANT_INVOKED"
    }
}
