package com.saphira.ai

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * Saphira Accessibility Service (Flutter-facing package).
 *
 * User must enable this service in Settings → Accessibility.
 * Mutation methods require a short-lived [authorize] token issued by the
 * backend policy layer (CommercialAuthorityPolicy / autonomy gate).
 *
 * © 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
 */
class SaphiraAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "SaphiraA11y"
        private const val AUTH_TTL_MS = 30_000L

        @Volatile
        var instance: SaphiraAccessibilityService? = null
            private set
    }

    private var authToken: String? = null
    private var authExpiresAt: Long = 0L

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.i(TAG, "SaphiraAccessibilityService connected")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Continuous screen state inspection hook — passive by default.
        // No screen contents are captured or persisted unless authorized.
    }

    override fun onInterrupt() {
        Log.w(TAG, "Service interrupted")
    }

    override fun onDestroy() {
        instance = null
        super.onDestroy()
    }

    // ── Authorization gate ──────────────────────────────────────────────────

    fun authorize(token: String, ttlMs: Long = AUTH_TTL_MS): Boolean {
        if (token.isBlank()) return false
        authToken = token
        authExpiresAt = System.currentTimeMillis() + ttlMs
        Log.i(TAG, "Authorized for ${ttlMs}ms")
        return true
    }

    fun revokeAuth() {
        authToken = null
        authExpiresAt = 0L
    }

    private fun isAuthorized(): Boolean {
        val ok = authToken != null && System.currentTimeMillis() < authExpiresAt
        if (!ok) Log.w(TAG, "Action rejected – not authorized or token expired")
        return ok
    }

    /**
     * Finds and clicks a button or UI element matching target text.
     */
    fun clickElementByText(targetText: String): Boolean {
        if (!isAuthorized()) return false
        val rootNode = rootInActiveWindow ?: return false
        return try {
            val matchingNodes = rootNode.findAccessibilityNodeInfosByText(targetText)
            if (matchingNodes.isNullOrEmpty()) return false

            for (node in matchingNodes) {
                if (node.isClickable) {
                    return node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                }
                // Traverse upward if parent wrapper holds the click listener
                var parent = node.parent
                while (parent != null) {
                    if (parent.isClickable) {
                        val ok = parent.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                        parent.recycle()
                        return ok
                    }
                    val next = parent.parent
                    parent.recycle()
                    parent = next
                }
            }
            false
        } finally {
            rootNode.recycle()
        }
    }

    /**
     * Injects text directly into an active focused input field.
     */
    fun injectTextIntoFocusedInput(text: String): Boolean {
        if (!isAuthorized()) return false
        val rootNode = rootInActiveWindow ?: return false
        return try {
            val focusedNode = rootNode.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: return false
            val arguments = Bundle().apply {
                putCharSequence(
                    AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                    text
                )
            }
            focusedNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
        } finally {
            rootNode.recycle()
        }
    }

    /**
     * Executes programmatic tap gesture at screen coordinates (X, Y).
     */
    fun performTapAtCoordinates(x: Float, y: Float): Boolean {
        if (!isAuthorized()) return false
        val path = Path().apply { moveTo(x, y) }
        val stroke = GestureDescription.StrokeDescription(path, 0, 100)
        val gesture = GestureDescription.Builder().addStroke(stroke).build()
        return dispatchGesture(gesture, null, null)
    }

    fun globalAction(name: String): Boolean {
        if (!isAuthorized()) return false
        val action = when (name.uppercase()) {
            "HOME" -> GLOBAL_ACTION_HOME
            "BACK" -> GLOBAL_ACTION_BACK
            "RECENTS" -> GLOBAL_ACTION_RECENTS
            "NOTIFICATIONS" -> GLOBAL_ACTION_NOTIFICATIONS
            else -> return false
        }
        return performGlobalAction(action)
    }
}
