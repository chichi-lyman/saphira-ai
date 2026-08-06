// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
package com.saphira.ai

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.voice.VoiceInteractionSession
import android.util.Log

class SaphiraVoiceInteractionSession(context: Context) : VoiceInteractionSession(context) {
    override fun onShow(args: Bundle?, showFlags: Int) {
        super.onShow(args, showFlags)
        Log.i(TAG, "Voice session shown")
        val intent = Intent(context, MainActivity::class.java).apply {
            action = SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED
            putExtra("show_overlay", true)
            putExtra("source", "voice_session")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }
        context.startActivity(intent)
        hide()
    }
    companion object { private const val TAG = "SaphiraVISSession" }
}
