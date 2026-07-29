// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// Default system voice assistant entry — user can set Saphira as assistant
// (home long-press / assistant gesture), similar to Gemini.

package com.saphira.ai

import android.content.Intent
import android.os.Bundle
import android.service.voice.VoiceInteractionService
import android.util.Log

class SaphiraVoiceInteractionService : VoiceInteractionService() {

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "SaphiraVoiceInteractionService created")
    }

    override fun onReady() {
        super.onReady()
        Log.i(TAG, "SaphiraVoiceInteractionService ready — system may invoke assistant")
        // Optional: warm Flutter engine / wake-word handoff
    }

    override fun onShutdown() {
        Log.i(TAG, "SaphiraVoiceInteractionService shutdown")
        super.onShutdown()
    }

    companion object {
        private const val TAG = "SaphiraVIS"

        /** Intent action Flutter / MainActivity can listen for when assistant is invoked. */
        const val ACTION_ASSISTANT_INVOKED = "com.saphira.ai.ACTION_ASSISTANT_INVOKED"
    }
}
