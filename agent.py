# import json

# # --- 1. ARAÇLAR (TOOLS) ---
# # Ajanın yapabileceği işler. Gerçek hayatta bu bir API çağrısı veya veritabanı sorgusudur.
# def get_weather(city: str) -> str:
#     """Belirtilen şehrin hava durumunu döner."""
#     weather_data = {
#         "kayseri": "18°C, Parçalı Bulutlu",
#         "istanbul": "22°C, Güneşli",
#         "ankara": "16°C, Yağmurlu"
#     }
#     return weather_data.get(city.lower(), "Bilinmiyor (Veri bulunamadı)")

# def calculate(expression: str) -> str:
#     """Basit bir matematiksel ifadeyi hesaplar."""
#     try:
#         # Gerçek prodüksiyonda eval yerine güvenli parser kullanılır
#         return str(eval(expression))
#     except Exception as e:
#         return f"Hata: {e}"

# # Modele sunduğumuz araç kayıt defteri
# AVAILABLE_TOOLS = {
#     "get_weather": get_weather,
#     "calculate": calculate
# }


# # --- 2. BEYİN (MOCK LLM REASONING) ---
# # Gerçekte bu kararı OpenAI/Claude gibi bir LLM verir. 
# # Mantığı anlamak için modelin üreteceği JSON çıktısını simüle ediyoruz.
# def mock_llm_decide(user_prompt: str) -> str:
#     """Kullanıcının isteğine göre hangi aracın çağrılacağına karar verir."""
#     prompt = user_prompt.lower()
    
#     if "hava" in prompt and "kayseri" in prompt:
#         return json.dumps({
#             "thought": "Kullanıcı Kayseri hava durumunu sordu. get_weather aracını çağırmalıyım.",
#             "tool": "get_weather",
#             "args": {"city": "Kayseri"}
#         })
#     elif "hesapla" in prompt or "+" in prompt or "*" in prompt:
#         return json.dumps({
#             "thought": "Kullanıcı bir matematik işlemi istedi. calculate aracını çağırmalıyım.",
#             "tool": "calculate",
#             "args": {"expression": "25 * 4"}
#         })
#     else:
#         return json.dumps({
#             "thought": "Özel bir araca gerek yok, doğrudan yanıt verebilirim.",
#             "tool": None,
#             "response": "Bu konuda yardımcı olamıyorum."
#         })


# # --- 3. YÜRÜTÜCÜ VE KARAR DÖNGÜSÜ (AGENT RUNNER) ---
# def run_agent(user_query: str):
#     print(f"\n[KULLANICI]: {user_query}")
    
#     # 1. Aşama: Düşün (Reason)
#     llm_decision = mock_llm_decide(user_query)
#     decision = json.loads(llm_decision)
    
#     print(f"[AJAN DÜŞÜNCESİ]: {decision.get('thought')}")
    
#     selected_tool = decision.get("tool")
    
#     # 2. Aşama: Harekete Geç (Act)
#     if selected_tool and selected_tool in AVAILABLE_TOOLS:
#         tool_func = AVAILABLE_TOOLS[selected_tool]
#         tool_args = decision.get("args", {})
        
#         print(f"[ARAÇ ÇAĞRILIYOR]: {selected_tool}({tool_args})")
        
#         # 3. Aşama: Gözlemle (Observe)
#         tool_result = tool_func(**tool_args)
#         print(f"[ARAÇ ÇIKTISI]: {tool_result}")
        
#         # Sonuç kullanıcıya iletilir
#         final_answer = f"İşlem tamamlandı. Sonuç: {tool_result}"
#     else:
#         final_answer = decision.get("response")
        
#     print(f"[AJAN YANITI]: {final_answer}\n" + "-"*40)


# if __name__ == "__main__":
#     # Test Senaryoları
#     run_agent("Kayseri'de bugün hava nasıl?")
#     run_agent("25 ile 4'ü çarpar mısın?")

import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. .env dosyasındaki GROQ_API_KEY'i çevre değişkenlerine yükle
load_dotenv()

# 2. Groq istemcisini başlat
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- BÖLÜM 1: ARAÇLAR (TOOLS) ---
def get_weather(city: str) -> str:
    weather_data = {
        "kayseri": "18°C, Parçalı Bulutlu",
        "istanbul": "22°C, Güneşli",
        "ankara": "16°C, Yağmurlu"
    }
    return weather_data.get(city.lower(), "Bilinmiyor (Veri bulunamadı)")

def calculate(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expression).issubset(allowed):
            return "Hata: Güvenlik nedeniyle geçersiz karakter."
        return str(eval(expression))
    except Exception as e:
        return f"Hata: {str(e)}"

# Araç Kayıt Defteri (Registry)
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate
}

# --- BÖLÜM 2: GERÇEK LLM BEYNİ (SYSTEM PROMPT & DECISION) ---
SYSTEM_PROMPT = """
Sen akıllı bir asistansın. Kullanıcının taleplerini analiz eder ve gerekirse araçları kullanırsın.

Kullanabileceğin araçlar:
1. get_weather(city: str): Bir şehrin hava durumunu getirir.
2. calculate(expression: str): Matematiksel ifadeleri hesaplar (Örn: "25 * 4").

KURALLAR:
- Yanıtını SADECE ve SADECE geçerli bir JSON formatında ver. Başka hiçbir açıklama, selamlama veya markdown bloğu (```json gibi) ekleme.
- Eğer bir araç kullanman gerekiyorsa şu formatı üret:
  {"thought": "Neden bu aracı seçtiğin", "tool": "araç_adı", "args": {"parametre_adı": "değer"}}
- Eğer bir araca gerek yoksa (örneğin sadece sohbet ediliyorsa) şu formatı üret:
  {"thought": "Araca gerek yok", "tool": null, "args": {}, "response": "Kullanıcıya vereceğin doğrudan cevap"}
"""

def llm_decide(user_prompt: str) -> str:
    """Kullanıcı mesajını Groq API üzerinden Llama-3 modeline gönderir ve JSON kararını alır."""
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        # YENİ HALİ:
        model="qwen/qwen3.8-27b",
        temperature=0.0  # Kararların tutarlı ve deterministik olması için sıfır yapıyoruz
    )
    return chat_completion.choices[0].message.content

# --- BÖLÜM 3: YÜRÜTÜCÜ (AGENT RUNNER) ---
def run_agent(user_query: str):
    print(f"\n[KULLANICI]: {user_query}")
    
    # Gerçek modele sor
    raw_decision = llm_decide(user_query)
    
    try:
        decision = json.loads(raw_decision)
    except json.JSONDecodeError:
        print(f"[HATA]: Model geçerli bir JSON üretemedi:\n{raw_decision}")
        return

    thought = decision.get("thought", "Düşünce belirtilmedi.")
    selected_tool = decision.get("tool")
    tool_args = decision.get("args", {})
    
    print(f"[AJAN DÜŞÜNCESİ]: {thought}")
    
    # Araç çağırma kontrolü
    if selected_tool and selected_tool in AVAILABLE_TOOLS:
        print(f"[ARAÇ ÇAĞRILIYOR]: {selected_tool}({tool_args})")
        tool_func = AVAILABLE_TOOLS[selected_tool]
        tool_result = tool_func(**tool_args)
        print(f"[ARAÇ ÇIKTISI]: {tool_result}")
        print(f"[AJAN YANITI]: İşlem tamamlandı. Sonuç: {tool_result}")
    else:
        direct_response = decision.get("response", "Nasıl yardımcı olabileceğimi anlayamadım.")
        print(f"[AJAN YANITI]: {direct_response}")

# --- BÖLÜM 4: TEST ---
if __name__ == "__main__":
    # 1. Test: Serbest metin hava durumu (Artık 'hava' kelimesi zorunlu değil!)
    run_agent("Kayseri'de dışarısı montluk mu, hava nasıl?")
    
    # 2. Test: Az önce 'çarpar mısın' dediğimizde patlayan matematik testi
    run_agent("25 ile 4'ü çarpar mısın?")
    
    # 3. Test: Hiçbir araca ihtiyaç duymayan normal bir sohbet
    run_agent("Selam, senin adın ne, ne işe yararsın?")