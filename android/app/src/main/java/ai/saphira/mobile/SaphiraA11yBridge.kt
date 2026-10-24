package ai.saphira.mobile

import android.util.Log
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel

/**
 * Flutter MethodChannel bridge for [SaphiraAccessibilityService].
 *
 * Channel name: "ai.saphira/accessibility"
 *
 * Methods:
 *   authorize(token, ttlMs?) → bool
 *   revokeAuth() → void
 *   dumpUiTree() → String (JSON)
 *   clickByText(text) → bool
 *   clickByViewId(viewId) → bool
 *   clickAt(x, y) → bool
 *   scroll(direction) → bool
 *   setText(viewId, text) → bool
 *   globalAction(name) → bool
 *   isAvailable() → bool
 *
 * Register from MainActivity / FlutterEngine:
 *   MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "ai.saphira/accessibility")
 *       .setMethodCallHandler(SaphiraA11yBridge())
 *
 * © 2026 Chelsea Megan Woods
 */
class SaphiraA11yBridge : MethodChannel.MethodCallHandler {

    companion object {
        const val CHANNEL = "ai.saphira/accessibility"
        private const val TAG = "SaphiraA11yBridge"
    }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        val svc = SaphiraAccessibilityService.instance
        if (svc == null && call.method != "isAvailable") {
            result.error("UNAVAILABLE", "Accessibility service not enabled", null)
            return
        }

        try {
            when (call.method) {
                "isAvailable" -> result.success(svc != null)

                "authorize" -> {
                    val token = call.argument<String>("token") ?: ""
                    val ttl = call.argument<Number>("ttlMs")?.toLong() ?: 30_000L
                    result.success(svc!!.authorize(token, ttl))
                }

                "revokeAuth" -> {
                    svc!!.revokeAuth()
                    result.success(null)
                }

                "dumpUiTree" -> result.success(svc!!.dumpUiTree())

                "clickByText" -> {
                    val text = call.argument<String>("text") ?: ""
                    result.success(svc!!.clickByText(text))
                }

                "clickByViewId" -> {
                    val id = call.argument<String>("viewId") ?: ""
                    result.success(svc!!.clickByViewId(id))
                }

                "clickAt" -> {
                    val x = call.argument<Double>("x")?.toFloat() ?: 0f
                    val y = call.argument<Double>("y")?.toFloat() ?: 0f
                    result.success(svc!!.clickAt(x, y))
                }

                "scroll" -> {
                    val dir = call.argument<String>("direction") ?: "down"
                    result.success(svc!!.scroll(dir))
                }

                "setText" -> {
                    val id = call.argument<String>("viewId") ?: ""
                    val text = call.argument<String>("text") ?: ""
                    result.success(svc!!.setText(id, text))
                }

                "globalAction" -> {
                    val name = call.argument<String>("name") ?: ""
                    result.success(svc!!.globalAction(name))
                }

                else -> result.notImplemented()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Method ${call.method} failed", e)
            result.error("ERROR", e.message, null)
        }
    }
}
