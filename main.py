from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import agent

# 1. FastAPI uygulamasını başlat
app = FastAPI(
    title="AI Core Agent API",
    description="ReAct tabanlı, araç kullanabilen otonom AI Agent servisi",
    version="1.0.0"
)

# 2. İstek (Request) Gövdesi için Şema Belirle
# Kullanıcıdan gelecek JSON formatını zorunlu tutuyoruz: {"query": "..."}
class ChatRequest(BaseModel):
    query: str

# 3. Sağlık Kontrolü (Healthcheck) Endpoint'i
# DevOps dünyasında AWS veya Docker konteynerinin ayakta olup olmadığını buradan izleriz.
@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Core Agent is running"}

# 4. Ajanı Tetikleyen Ana Chat Endpoint'i
@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    try:
        # Gelen metni bizim agent.py içindeki motora gönderiyoruz
        user_query = request.query
        
        # Karar mekanizması ve çalıştırma
        raw_decision = agent.llm_decide(user_query)
        import json
        decision = json.loads(raw_decision)
        
        selected_tool = decision.get("tool")
        tool_args = decision.get("args", {})
        thought = decision.get("thought", "")
        
        # Araç varsa çalıştır
        if selected_tool and selected_tool in agent.AVAILABLE_TOOLS:
            tool_func = agent.AVAILABLE_TOOLS[selected_tool]
            tool_result = tool_func(**tool_args)
            final_response = f"İşlem tamamlandı. Sonuç: {tool_result}"
        else:
            final_response = decision.get("response", "Yanıt üretilemedi.")
            
        return {
            "query": user_query,
            "thought": thought,
            "tool_used": selected_tool,
            "tool_args": tool_args,
            "response": final_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))