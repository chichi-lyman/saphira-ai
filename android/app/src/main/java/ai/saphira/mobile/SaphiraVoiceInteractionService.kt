package ai.saphira.mobile

import android.service.voice.VoiceInteractionService
import android.service.voice.VoiceInteractionSession

class SaphiraVoiceInteractionService : VoiceInteractionService() {
    override fun onReady() {
        super.onReady()
    }

    override fun onNewSession(args: android.os.Bundle?): VoiceInteractionSession {
        return SaphiraVoiceSession(this)
    }
}

class SaphiraVoiceSession(service: VoiceInteractionService) : VoiceInteractionSession(service) {
    override fun onShow(args: android.os.Bundle?, showFlags: Int) {
        super.onShow(args, showFlags)
    }
}
