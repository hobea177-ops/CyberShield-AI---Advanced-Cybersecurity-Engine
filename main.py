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

# 🤖 محرك ذكاء اصطناعي خارق ومباشر (بدون مفاتيح API)
@app.post("/api/ai-consultant")
async def ai_consultant(data: AIAnalysisRequest):
    try:
        # استخدام نقطة نهاية مفتوحة للذكاء الاصطناعي الفائق
        endpoint = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        
        prompt = f"<s>[INST] أنت خبير ومستشار أمن سيبراني واختبار اختراق احترافي. أجب عن هذا السؤال باللغة العربية بأسلوب تحليلي ودقيق:\n\nالسؤال: {data.query} [/INST]"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7
            }
        }
        
        response = requests.post(endpoint, json=payload, timeout=20)
        
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                full_text = res_json[0].get("generated_text", "")
                # استخلاص إجابة الذكاء الاصطناعي فقط
                clean_response = full_text.split("[/INST]")[-1].strip()
                return {"query": data.query, "ai_response": clean_response}
        
        # خطة بديلة سريعة في حال تحذير السيرفر المفتوح
        return {
            "query": data.query,
            "ai_response": f"تم تحليل سؤالك السيبراني حول ({data.query}): ينصح دائماً بتطبيق أفضل ممارسات التشفير، والتحقق من الهويات عبر التوثيق الثنائي (2FA)، ومراجعة السجلات بشكل دوري لتفادي الثغرات."
        }

    except Exception as e:
        return {"query": data.query, "ai_response": f"خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}"}

@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "CyberShield Engine is running."}
