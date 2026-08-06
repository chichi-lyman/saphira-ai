// Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
package com.saphira.ai

import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.provider.Settings
import android.util.Log

object SaphiraRoleHelper {
    private const val TAG = "SaphiraRole"

    fun isRoleApiAvailable(): Boolean = Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q

    fun roleManager(context: Context): RoleManager? {
        if (!isRoleApiAvailable()) return null
        return context.getSystemService(RoleManager::class.java)
    }

    fun isAssistantRoleAvailable(context: Context): Boolean {
        val rm = roleManager(context) ?: return false
        return try { rm.isRoleAvailable(RoleManager.ROLE_ASSISTANT) } catch (e: Exception) {
            Log.w(TAG, "isRoleAvailable failed", e); false
        }
    }

    fun isAssistantRoleHeld(context: Context): Boolean {
        val rm = roleManager(context) ?: return false
        return try { rm.isRoleHeld(RoleManager.ROLE_ASSISTANT) } catch (e: Exception) {
            Log.w(TAG, "isRoleHeld failed", e); false
        }
    }

    fun createRequestRoleIntent(context: Context): Intent? {
        val rm = roleManager(context) ?: return null
        if (!rm.isRoleAvailable(RoleManager.ROLE_ASSISTANT)) return null
        if (rm.isRoleHeld(RoleManager.ROLE_ASSISTANT)) return null
        return try { rm.createRequestRoleIntent(RoleManager.ROLE_ASSISTANT) } catch (e: Exception) {
            Log.w(TAG, "createRequestRoleIntent failed", e); null
        }
    }

    fun openVoiceInputSettings(context: Context) {
        val intents = listOf(
            Intent(Settings.ACTION_VOICE_INPUT_SETTINGS),
            Intent(Settings.ACTION_MANAGE_DEFAULT_APPS_SETTINGS),
            Intent(Settings.ACTION_SETTINGS)
        )
        for (intent in intents) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            try { context.startActivity(intent); return } catch (_: Exception) {}
        }
    }

    fun statusMap(context: Context): Map<String, Any?> = mapOf(
        "apiAvailable" to isRoleApiAvailable(),
        "roleAvailable" to isAssistantRoleAvailable(context),
        "roleHeld" to isAssistantRoleHeld(context),
        "sdk" to Build.VERSION.SDK_INT
    )
}
