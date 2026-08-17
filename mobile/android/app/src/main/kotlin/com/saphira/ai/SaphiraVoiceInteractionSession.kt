// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
// Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
//
// VoiceInteractionSession with compact dark overlay UI and AssistStructure capture.
// Provides the system-level entry path that lets Saphira act as a true device assistant.

package com.saphira.ai

import android.app.assist.AssistStructure
import android.content.Context
import android.content.Intent
import android.os.Build
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

    /** Lightweight summary of the screen the user was looking at when assist was invoked. */
    private var lastAssistSummary: String = ""
    private var lastPackageName: String? = null
    private var lastActivityClass: String? = null

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
        Log.i(TAG, "Session shown — flags=$showFlags")
        setUiEnabled(true)
        statusView?.text = "Ready"
        updateTranscriptForContext()
        listening = false
    }

    override fun onHide() {
        Log.i(TAG, "Session hidden")
        listening = false
        super.onHide()
    }

    /**
     * Called by the system when the user invokes the assistant (long-press home / power,
     * assist gesture, etc.). Provides the current window hierarchy so Saphira can reason
     * about what the user is looking at.
     */
    override fun onHandleAssist(state: AssistState) {
        super.onHandleAssist(state)
        Log.i(TAG, "onHandleAssist invoked")

        val structure = state.assistStructure
        if (structure != null) {
            captureAssistStructure(structure)
        } else {
            lastAssistSummary = ""
            lastPackageName = null
            lastActivityClass = null
        }

        // Refresh overlay text with any context we just captured
        updateTranscriptForContext()
    }

    /**
     * Older API path still used on some devices / Android versions.
     */
    @Deprecated("Deprecated in Java")
    override fun onHandleAssist(
        data: Bundle?,
        structure: AssistStructure?,
        content: android.app.assist.AssistContent?
    ) {
        @Suppress("DEPRECATION")
        super.onHandleAssist(data, structure, content)
        Log.i(TAG, "onHandleAssist (legacy) invoked")
        if (structure != null) {
            captureAssistStructure(structure)
            updateTranscriptForContext()
        }
    }

    private fun captureAssistStructure(structure: AssistStructure) {
        try {
            val windowCount = structure.windowNodeCount
            if (windowCount <= 0) {
                lastAssistSummary = ""
                return
            }

            val window = structure.getWindowNodeAt(0)
            lastPackageName = window?.title?.toString()
            // Activity class is not always present; package + root text is still useful.

            val root = window?.rootViewNode
            val textSnippets = mutableListOf<String>()
            if (root != null) {
                collectTextNodes(root, textSnippets, maxDepth = 6, maxItems = 12)
            }

            lastAssistSummary = buildString {
                append("Screen context")
                if (!lastPackageName.isNullOrBlank()) {
                    append(" (")
                    append(lastPackageName)
                    append(")")
                }
                if (textSnippets.isNotEmpty()) {
                    append(": ")
                    append(textSnippets.take(6).joinToString(" · "))
                }
            }.take(280)

            Log.i(TAG, "AssistStructure captured: windows=$windowCount summaryLen=${lastAssistSummary.length}")
        } catch (e: Exception) {
            Log.w(TAG, "Failed to walk AssistStructure", e)
            lastAssistSummary = ""
        }
    }

    private fun collectTextNodes(
        node: AssistStructure.ViewNode,
        out: MutableList<String>,
        maxDepth: Int,
        maxItems: Int,
        depth: Int = 0
    ) {
        if (depth > maxDepth || out.size >= maxItems) return

        val text = node.text?.toString()?.trim().orEmpty()
        val contentDesc = node.contentDescription?.toString()?.trim().orEmpty()
        val candidate = when {
            text.isNotEmpty() && text.length in 2..80 -> text
            contentDesc.isNotEmpty() && contentDesc.length in 2..80 -> contentDesc
            else -> null
        }
        if (candidate != null && !out.contains(candidate)) {
            out.add(candidate)
        }

        for (i in 0 until node.childCount) {
            if (out.size >= maxItems) break
            val child = node.getChildAt(i) ?: continue
            collectTextNodes(child, out, maxDepth, maxItems, depth + 1)
        }
    }

    private fun updateTranscriptForContext() {
        if (lastAssistSummary.isNotBlank()) {
            transcriptView?.text = lastAssistSummary
            statusView?.text = "Context captured"
        } else {
            transcriptView?.text =
                "Tap the mic or say something. Open the full app for the complete experience."
        }
    }

    private fun toggleListening() {
        listening = !listening
        if (listening) {
            statusView?.text = "Listening…"
            transcriptView?.text = "Speak now — Saphira is listening."
            Log.i(TAG, "Listening started (SpeechRecognizer wiring is next)")
        } else {
            statusView?.text = "Ready"
            updateTranscriptForContext()
            Log.i(TAG, "Listening stopped")
        }
    }

    private fun openFullApp() {
        Log.i(TAG, "Opening full Flutter activity with assist context")
        val intent = Intent(context, MainActivity::class.java).apply {
            action = SaphiraVoiceInteractionService.ACTION_ASSISTANT_INVOKED
            putExtra("show_overlay", true)
            putExtra("source", "voice_session_overlay")
            putExtra("assist_summary", lastAssistSummary)
            putExtra("assist_package", lastPackageName)
            putExtra("triggered_by_assistant", true)
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
