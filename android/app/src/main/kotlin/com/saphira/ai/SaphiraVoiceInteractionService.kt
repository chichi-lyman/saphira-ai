// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Default Voice Assistant hook — register in AndroidManifest with BIND_VOICE_INTERACTION

package com.saphira.ai

import android.service.voice.VoiceInteractionService

/**
 * Allows the user to set Saphira as the device default assistant
 * (home long-press / gesture), similar to Gemini / Google Assistant.
 *
 * Pair with res/xml/voice_interaction_service.xml and Flutter overlay launch.
 */
class SaphiraVoiceInteractionService : VoiceInteractionService() {
    override fun onReady() {
        super.onReady()
        // Notify Flutter / start session when system invokes assistant
    }
}
