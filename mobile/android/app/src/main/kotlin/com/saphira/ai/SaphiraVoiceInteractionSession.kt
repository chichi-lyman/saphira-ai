// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// VoiceInteractionSession with a compact dark overlay UI.
// Can also launch the full Flutter MainActivity on demand.

package com.saphira.ai

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.voice.VoiceInteractionSession
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView

class SaphiraVoiceInteractionSession(context: Context) : VoiceInteractionSession(context) {

    private var statusView: TextView? = null
    private var transcriptView: TextView? = null
    private var micButton: ImageButton? = null
    private var listening = false

    override fun onCreateContentView(): View {
        val pkg = context.packageName
        val view = layoutInflater.inflate(
            context.resources.getIdentifier("saphira_voice_overlay", "layout", pkg),
            null
        )

        statusView = view.findViewById(context.resources.getIdentifier("saphira_status", "id", pkg))
        transcriptView = view.findViewById(context.resources.getIdentifier("saphira_transcript", "id", pkg))
        micButton = view.findViewById(context.resources.getIdentifier("saphira_btn_mic", "id", pkg))

        view.findViewById<ImageButton>(
            context.resources.getIdentifier("saphira_btn_close", "id", pkg)
        )?.setOnClickListener { finishSession() }

        view.findViewById<Button>(
            context.resources.getIdentifier("saphira_btn_done", "id", pkg)
        )?.setOnClickListener { finishSession() }

        view.findViewById<Button>(
            context.resources.getIdentifier("saphira_btn_open_app", "id", pkg)
        )?.setOnClickListener { openFullApp() }

        micButton?.setOnClickListener { toggleListening() }

        return view
    }

    override fun onShow(args: Bundle?, showFlags: Int) {
        super.onShow(args, showFlags)
        Log.i(TAG, "Session shown \u2014 flags=$showFlags")
        setUiEnabled(true)
        statusView?.text = "Ready"
        transcriptView?.text = "Tap the mic or say something. Open the full app for the complete experience."
        listening = false
    }

    override fun onHide() {
        Log.i(TAG, "Session hidden")
        listening = false
        super.onHide()
    }

    private fun toggleListening() {
        listening = !listening
        if (listening) {
            statusView?.text = "Listening\u2026"
            transcriptView?.text = "Speak now \u2014 Saphira is listening."
            Log.i(TAG, "Listening started (stub \u2014 wire SpeechRecognizer next)")
        } else {
            statusView?.text = "Ready"
            transcriptView?.text = "Tap the mic or open the full app."
            Log.i(TAG, "Listening stopped")
        }
    }

    private fun openFullApp() {
        Log.i(TAG, "Opening full Flutter activity")
        val intent = Intent(context, MainActivity::class.java).apply {
            action = SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED
            putExtra("show_overlay", true)
            putExtra("source", "voice_session_overlay")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }
        try {
            startAssistantActivity(intent)
        } catch (e: Exception) {
            Log.w(TAG, "startAssistantActivity failed, falling back", e)
            context.startActivity(intent)
        }
        hide()
    }

    private fun finishSession() {
        Log.i(TAG, "Finishing session")
        listening = false
        hide()
        try {
            finish()
        } catch (e: Exception) {
            Log.w(TAG, "finish() error: ${e.message}")
        }
    }

    companion object {
        private const val TAG = "SaphiraVISSession"
    }
}
