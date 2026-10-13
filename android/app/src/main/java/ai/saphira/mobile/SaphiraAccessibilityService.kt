package ai.saphira.mobile

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.graphics.Rect
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import org.json.JSONArray
import org.json.JSONObject

/**
 * Saphira Accessibility Service
 * ----------------------------
 * Explicitly user-enabled bridge for screen-aware actions.
 *
 * Security model:
 *  - Passive by default; does NOT capture or persist screen contents.
 *  - All mutation methods require a prior [authorize] call that carries a
 *    short-lived token issued by the backend CommercialAuthorityPolicy /
 *    autonomy layer.
 *  - Tokens expire after [AUTH_TTL_MS]; subsequent calls without re-auth are rejected.
 *
 * Exposed capabilities (invoked via MethodChannel or bound binder):
 *  - dumpUiTree()          → JSON hierarchy for the backend planner
 *  - click(text|viewId|x,y)
 *  - scroll(direction)
 *  - setText(viewId, text)
 *  - globalAction(HOME|BACK|RECENTS|NOTIFICATIONS)
 *
 * © 2026 Chelsea Megan Woods / Woods AI Studio / Nova Umbrella
 */
class SaphiraAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "SaphiraA11y"
        private const val AUTH_TTL_MS = 30_000L

        /** Singleton handle so MethodChannel / binder can reach the live service. */
        @Volatile
        var instance: SaphiraAccessibilityService? = null
            private set
    }

    private var authToken: String? = null
    private var authExpiresAt: Long = 0L

    // ── Lifecycle ───────────────────────────────────────────────────────────

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.i(TAG, "SaphiraAccessibilityService connected")
    }

    override fun onDestroy() {
        instance = null
        super.onDestroy()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Intentionally passive – no screen content is captured or logged.
        // Future: optional event bus for backend-authorized observation only.
    }

    override fun onInterrupt() {
        Log.w(TAG, "Service interrupted")
    }

    // ── Authorization gate ──────────────────────────────────────────────────

    /**
     * Called by the Flutter / native bridge after the backend issues an
     * ALLOW decision. Token is opaque; only presence + TTL is checked here.
     */
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

    // ── UI tree dump (read-only, still gated) ───────────────────────────────

    fun dumpUiTree(): String {
        if (!isAuthorized()) return JSONObject().put("error", "unauthorized").toString()
        val root = rootInActiveWindow ?: return JSONObject().put("error", "no_root").toString()
        return try {
            nodeToJson(root).toString()
        } finally {
            root.recycle()
        }
    }

    private fun nodeToJson(node: AccessibilityNodeInfo): JSONObject {
        val obj = JSONObject()
        obj.put("class", node.className ?: "")
        obj.put("text", node.text?.toString() ?: "")
        obj.put("desc", node.contentDescription?.toString() ?: "")
        obj.put("viewId", node.viewIdResourceName ?: "")
        obj.put("clickable", node.isClickable)
        obj.put("editable", node.isEditable)
        obj.put("scrollable", node.isScrollable)
        val bounds = Rect()
        node.getBoundsInScreen(bounds)
        obj.put("bounds", JSONObject().apply {
            put("l", bounds.left); put("t", bounds.top)
            put("r", bounds.right); put("b", bounds.bottom)
        })
        val children = JSONArray()
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            children.put(nodeToJson(child))
            child.recycle()
        }
        obj.put("children", children)
        return obj
    }

    // ── Click ───────────────────────────────────────────────────────────────

    fun clickByText(text: String): Boolean {
        if (!isAuthorized()) return false
        val root = rootInActiveWindow ?: return false
        return try {
            val nodes = root.findAccessibilityNodeInfosByText(text)
            nodes.firstOrNull { it.isClickable }?.let { performClick(it) }
                ?: nodes.firstOrNull()?.let { clickParent(it) }
                ?: false
        } finally {
            root.recycle()
        }
    }

    fun clickByViewId(viewId: String): Boolean {
        if (!isAuthorized()) return false
        val root = rootInActiveWindow ?: return false
        return try {
            val nodes = root.findAccessibilityNodeInfosByViewId(viewId)
            nodes.firstOrNull()?.let { performClick(it) } ?: false
        } finally {
            root.recycle()
        }
    }

    fun clickAt(x: Float, y: Float): Boolean {
        if (!isAuthorized()) return false
        val path = Path().apply { moveTo(x, y) }
        val stroke = GestureDescription.StrokeDescription(path, 0, 50)
        val gesture = GestureDescription.Builder().addStroke(stroke).build()
        return dispatchGesture(gesture, null, null)
    }

    private fun performClick(node: AccessibilityNodeInfo): Boolean {
        return if (node.isClickable) {
            node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
        } else {
            clickParent(node)
        }
    }

    private fun clickParent(node: AccessibilityNodeInfo): Boolean {
        var current: AccessibilityNodeInfo? = node.parent
        while (current != null) {
            if (current.isClickable) {
                val ok = current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                current.recycle()
                return ok
            }
            val next = current.parent
            current.recycle()
            current = next
        }
        return false
    }

    // ── Scroll ──────────────────────────────────────────────────────────────

    fun scroll(direction: String): Boolean {
        if (!isAuthorized()) return false
        val root = rootInActiveWindow ?: return false
        return try {
            val action = when (direction.lowercase()) {
                "up", "forward" -> AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
                "down", "backward" -> AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
                else -> return false
            }
            findScrollable(root)?.performAction(action) ?: false
        } finally {
            root.recycle()
        }
    }

    private fun findScrollable(node: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        if (node.isScrollable) return node
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val found = findScrollable(child)
            if (found != null) return found
            child.recycle()
        }
        return null
    }

    // ── Text injection ──────────────────────────────────────────────────────

    fun setText(viewId: String, text: String): Boolean {
        if (!isAuthorized()) return false
        val root = rootInActiveWindow ?: return false
        return try {
            val nodes = root.findAccessibilityNodeInfosByViewId(viewId)
            val target = nodes.firstOrNull { it.isEditable } ?: nodes.firstOrNull() ?: return false
            val args = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
            }
            target.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        } finally {
            root.recycle()
        }
    }

    // ── Global actions ──────────────────────────────────────────────────────

    fun globalAction(name: String): Boolean {
        if (!isAuthorized()) return false
        val action = when (name.uppercase()) {
            "HOME" -> GLOBAL_ACTION_HOME
            "BACK" -> GLOBAL_ACTION_BACK
            "RECENTS" -> GLOBAL_ACTION_RECENTS
            "NOTIFICATIONS" -> GLOBAL_ACTION_NOTIFICATIONS
            "QUICK_SETTINGS" -> GLOBAL_ACTION_QUICK_SETTINGS
            else -> return false
        }
        return performGlobalAction(action)
    }
}
