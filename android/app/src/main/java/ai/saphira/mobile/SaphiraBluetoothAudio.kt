package ai.saphira.mobile

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothProfile
import android.content.Context
import android.content.pm.PackageManager

class SaphiraBluetoothAudio(private val context: Context) {
    fun connectedHeadsetCount(): Int {
        if (android.os.Build.VERSION.SDK_INT >= 31 &&
            context.checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED
        ) return 0
        val adapter = BluetoothAdapter.getDefaultAdapter() ?: return 0
        return runCatching {
            adapter.getProfileConnectionState(BluetoothProfile.HEADSET)
                .let { if (it == BluetoothProfile.STATE_CONNECTED) 1 else 0 }
        }.getOrDefault(0)
    }
}
