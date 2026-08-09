package ai.saphira.mobile

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

/**
 * Explicit user-enabled bridge for screen-aware actions. It is intentionally
 * passive until a future tool invocation is authorized by Saphira's policy layer.
 */
class SaphiraAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Do not capture or persist screen contents by default.
    }

    override fun onInterrupt() = Unit
}
