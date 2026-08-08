# Saphira AI Production Deployment Checklist

© 2026 Chelsea Megan Woods. All rights reserved.

## Overview

This document covers all critical configuration and integration points for deploying Saphira AI across:
- Python FastAPI backend (Railway)
- Flutter mobile app (Android + iOS)
- Web frontend (Vercel/Next.js)
- Local smart home hub (Home Assistant/Matter)

---

## 1. Backend Deployment (Railway)

### Environment Variables

Set these in Railway dashboard:

```bash
# Core Configuration
NODE_ENV=production
RAILWAY_PUBLIC_DOMAIN=your-saphira-production.railway.app
VERCEL_URL=saphira-delta.vercel.app

# API Keys (keep secret!)
GEMINI_API_KEY=<your_gemini_key>
OPENAI_API_KEY=<your_openai_key>
ANTHROPIC_API_KEY=<your_claude_key>

# Voice Synthesis
ELEVENLABS_API_KEY=<your_elevenlabs_key>
ELEVENLABS_VOICE_ID=<your_chelsea_voice_id>
SAPHIRA_TTS_PROVIDER=elevenlabs

# Database
DATABASE_URL=postgresql://user:pass@host:5432/saphira_db

# Smart Home
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_LONG_LIVED_TOKEN=<your_ha_token>
CONSOLE_BRIDGE_IP=192.168.1.99

# Wearables
WEARABLE_API_KEY=<optional>

# Messaging
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_CHAT_ID=<your_chat_id>
TWILIO_ACCOUNT_SID=<your_sid>
TWILIO_AUTH_TOKEN=<your_auth_token>

# Music
SPOTIFY_CLIENT_ID=<your_client_id>
SPOTIFY_CLIENT_SECRET=<your_client_secret>

# Performance
AGENT_ZERO_MAX_MEMORY_GB=8
DEVICE_COMMAND_TIMEOUT=2.5
MAX_DEVICE_RETRIES=2
LYRA_COMPLIANCE_MODE=STRICT_CLAMP
```

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git push origin feature/async-device-queue
   # OR merge to main for auto-deploy
   git checkout main
   git merge feature/async-device-queue
   git push origin main
   ```

2. **Railway Dashboard**
   - Connect GitHub repo (if not already connected)
   - Set environment variables above
   - Railway auto-deploys on `main` branch push

3. **Verify Deployment**
   ```bash
   curl https://your-saphira-production.railway.app/
   # Should return: {"message": "Welcome to Saphira AI", "status": "running"}
   
   curl https://your-saphira-production.railway.app/health
   # Should return: {"status": "healthy"}
   ```

### Health Checks

Railway will automatically restart the container if:
- Health check fails for 3 consecutive attempts
- Container crashes

---

## 2. Frontend Deployment (Vercel)

### Environment Variables

Set in Vercel dashboard:

```bash
# Backend Connection
NEXT_PUBLIC_API_URL=https://your-saphira-production.railway.app
REACT_APP_API_URL=https://your-saphira-production.railway.app

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_BIOMETRICS=true
NEXT_PUBLIC_ENABLE_IOT=true

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=<your_analytics_id>
```

### Deployment Steps

1. **Push to GitHub**
   ```bash
   # Push to main branch (or your deployment branch)
   git push origin main
   ```

2. **Vercel Auto-Deploy**
   - Vercel automatically deploys on push to main
   - Check deployment status at vercel.com dashboard

3. **Verify Frontend**
   ```bash
   # Visit https://saphira-delta.vercel.app
   # Should load without CORS errors
   # Check browser console for any connection errors
   ```

### CORS Testing

In browser console:
```javascript
fetch('https://your-saphira-production.railway.app/config')
  .then(r => r.json())
  .then(d => console.log('CORS OK:', d))
  .catch(e => console.error('CORS ERROR:', e))
```

Should show:
```
CORS OK: {
  api_url: "...",
  environment: "production",
  cors_enabled: true,
  features: {...}
}
```

---

## 3. Mobile Deployment (Android)

### AndroidManifest.xml Checklist

Ensure these permissions exist:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" ...>
  
  <!-- Voice Interaction Permissions -->
  <uses-permission android:name="android.permission.BIND_VOICE_INTERACTION" />
  <uses-permission android:name="android.permission.RECORD_AUDIO" />
  <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
  
  <!-- Network Permissions -->
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
  
  <!-- Device Control Permissions -->
  <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
  <uses-permission android:name="android.permission.CAMERA" />
  
  <application ...>
    <!-- Voice Service Declaration -->
    <service
      android:name=".VoiceServiceBridge"
      android:permission="android.permission.BIND_VOICE_INTERACTION"
      android:exported="true">
      <intent-filter>
        <action android:name="android.service.voice.VoiceInteractionService" />
      </intent-filter>
    </service>
    
    <!-- Activities -->
    <activity android:name=".MainActivity" ...>
      ...
    </activity>
  </application>
</manifest>
```

### Flutter Platform Channel Setup

**Kotlin Side** (`MainActivity.kt`):
```kotlin
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
  companion object {
    private const val CHANNEL = "com.saphira/voice_service"
  }
  
  override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
    super.configureFlutterEngine(flutterEngine)
    
    MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
      .setMethodCallHandler { call, result ->
        try {
          when (call.method) {
            "initialize" -> {
              // Initialize voice service
              result.success("Voice service ready")
            }
            "processAudio" -> {
              val audio = call.argument<ByteArray>("audio")
              // Process audio with timeout protection
              result.success("Audio processed")
            }
            else -> result.notImplemented()
          }
        } catch (e: Exception) {
          result.error("ERROR", e.message, null)
        }
      }
  }
}
```

### Testing Voice Service

1. **Build and install**
   ```bash
   flutter pub get
   flutter build apk --release
   adb install build/app/outputs/apk/release/app-release.apk
   ```

2. **Test voice input**
   ```bash
   adb shell am instrument -w com.saphira.test/androidx.test.runner.AndroidJUnitRunner
   ```

3. **Check logs**
   ```bash
   adb logcat | grep SaphiraVoice
   # Should show: "Voice service created", "Voice service initialized"
   ```

---

## 4. Smart Home Hub Setup (Local Network)

### Home Assistant Configuration

1. **Verify Home Assistant is running**
   ```bash
   # On your hub device
   curl http://192.168.1.100:8123/api/ -H "Authorization: Bearer <token>"
   ```

2. **Create long-lived token**
   - Go to http://192.168.1.100:8123
   - Account → Create Long-Lived Access Token
   - Copy token to `HOME_ASSISTANT_LONG_LIVED_TOKEN`

3. **Test connection from Saphira**
   ```bash
   curl -H "Authorization: Bearer <token>" \
     http://192.168.1.100:8123/api/states
   # Should return list of entities
   ```

### Device Timeout Configuration

In Saphira environment:
```bash
DEVICE_COMMAND_TIMEOUT=2.5        # Max wait per device
MAX_DEVICE_RETRIES=2              # Max retries per command
```

This prevents:
- ✓ Offline devices blocking conversation
- ✓ Infinite retry loops
- ✓ Light blinking multiple times

---

## 5. Security Hardening

### Environment File Protection

```bash
# Ensure .env files are never committed
cat .gitignore
# Should contain:
# .env
# .env.*.local
# secrets/
```

### API Key Rotation

Rotate these monthly:
- `OPENAI_API_KEY` → platform.openai.com
- `GEMINI_API_KEY` → console.cloud.google.com
- `ELEVENLABS_API_KEY` → elevenlabs.io dashboard
- `HOME_ASSISTANT_LONG_LIVED_TOKEN` → Home Assistant UI

### Network Security

1. **Home Assistant not exposed to internet**
   ```bash
   # Verify port 8123 is NOT publicly accessible
   nmap -p 8123 your-public-ip
   # Should show: filtered or closed
   ```

2. **VPN for remote access** (optional)
   ```bash
   # Use Tailscale or Wireguard instead of port forwarding
   ```

---

## 6. Monitoring & Debugging

### Log Access

**Backend Logs** (Railway):
```bash
# In Railway dashboard → Deployments → Logs
# Or via CLI:
railway logs --follow
```

**Mobile Logs** (Android):
```bash
adb logcat | grep -E "SaphiraVoice|SaphiraDevice|Flutter"
```

### Key Metrics to Monitor

```bash
# API Response Times
curl -w "@curl-format.txt" https://your-saphira-production.railway.app/config

# Device Command Times
# Check logs for: "[{command_id}] Success in {elapsed_ms}ms"

# Error Rates
# Monitor: TimeoutError, PlatformException, JSONDecodeError
```

### Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| **CORS Error** | Frontend can't connect | Check `ALLOWED_ORIGINS` in main.py |
| **Voice Crash** | Android app crashes on voice | Check `AndroidManifest.xml` permissions |
| **Device Timeout** | Smart lights slow to respond | Increase `DEVICE_COMMAND_TIMEOUT` to 3.5 |
| **Cold Start Slow** | First message takes 5+ seconds | Enable context compression (TODO) |
| **Container Restarts** | Railway keeps restarting | Check container logs, increase memory |

---

## 7. Post-Deployment Validation

### Full System Test

```bash
# 1. Backend health
curl https://your-saphira-production.railway.app/health

# 2. Frontend loads
open https://saphira-delta.vercel.app

# 3. Frontend → Backend connection
# Open browser console, run:
fetch('https://your-saphira-production.railway.app/config').then(r => r.json()).then(console.log)

# 4. Home Assistant connected
# Should see devices in Saphira UI

# 5. Mobile voice works
# Say "Saphira, turn on the lights"
# Check AndroidLogcat for: "Voice service initialized"
```

### Sign-Off

- [ ] Backend deployed and healthy
- [ ] Frontend loads without CORS errors
- [ ] CORS headers correct
- [ ] Mobile voice service initialized
- [ ] Home Assistant devices visible
- [ ] Device command timeout working (< 2.5s)
- [ ] Logs accessible and clean
- [ ] API keys rotated
- [ ] Security checklist complete

---

## Support & Contact

**Issues?** Check:
1. Railway logs: `railway logs --follow`
2. Vercel dashboard: vercel.com/dashboard
3. Android logs: `adb logcat | grep Saphira`
4. Home Assistant: http://192.168.1.100:8123 (local only)

**Author:** Chelsea Megan Woods  
**Studio:** Woods AI Studio / Lyman Legacies  
**Copyright © 2026**
