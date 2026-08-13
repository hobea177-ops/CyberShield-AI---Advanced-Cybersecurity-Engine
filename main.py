from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import urllib.parse
import os

app = FastAPI(title="CyberShield AI - Direct Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 المفتاح الحر الخاص بك
GEMINI_KEY = "AQ.Ab8RN6K8Iab_d90cv_b_Lxj4DFVyqzK8D2rTXzJNSFOG6i0QDg"

class AuditRequest(BaseModel):
    url: str

class AIAnalysisRequest(BaseModel):
    query: str

@app.post("/api/audit")
async def audit_target(data: AuditRequest):
    try:
        parsed_url = urllib.parse.urlparse(data.url)
        domain = parsed_url.netloc or parsed_url.path.split('/')[0]
        is_https = data.url.startswith("https://")
        suspicious_keywords = ["login", "verify", "bank", "free", "mod", "happy", "update", "account", "apk"]
        has_suspicious_words = any(word in data.url.lower() for word in suspicious_keywords)
        
        risk_score = 10
        if not is_https: risk_score += 30
        if has_suspicious_words: risk_score += 35
        if "bit.ly" in data.url or "tinyurl" in data.url: risk_score += 25

        status = "SECURE" if risk_score < 30 else ("WARNING" if risk_score < 60 else "CRITICAL_RISK")

        return {
            "status": "success",
            "domain": domain,
            "protocol": "HTTPS" if is_https else "HTTP",
            "risk_score": risk_score,
            "security_status": status,
            "recommended_action": "تجنب إدخال أي بيانات حساسة." if risk_score >= 50 else "الرابط يبدو آمن الاستخدام."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ai-consultant")
async def ai_consultant(data: AIAnalysisRequest):
    try:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"أنت مستشار وخبير أمن سيبراني واختبار اختراق احترافي. أجب عن سؤال المستخدم بشكل دقيق ومفصل ومخصص باللغة العربية:\n\nالسؤال: {data.query}"
                }]
            }]
        }
        
        response = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        res_json = response.json()

        if response.status_code == 200 and "candidates" in res_json:
            ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
            return {"query": data.query, "ai_response": ai_text}
        else:
            err_msg = res_json.get("error", {}).get("message", "خطأ في الاستجابة")
            return {"query": data.query, "ai_response": f"خطأ من سيرفر الذكاء الاصطناعي: {err_msg}"}

    except Exception as e:
        return {"query": data.query, "ai_response": f"حدث خطأ بالنظام: {str(e)}"}

@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "CyberShield Engine is running."}
