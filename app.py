from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
Bạn là ShockAlert Assistant – chatbot CSKH chính thức của công ty
sản xuất túi ShockAlert Smart Bag.

Nhiệm vụ:
- Tra cứu đơn hàng
- Tư vấn túi chống sốc thông minh
- Hỏi thêm khi thiếu thông tin
- Không bịa đặt
- Nếu khách hỏi số lượng lớn → gợi ý báo giá

Giọng điệu: chuyên nghiệp, thân thiện
"""

ORDERS = {
    "SA-2025-1023": {
        "status": "Đang vận chuyển",
        "carrier": "GHTK",
        "eta": "12/01/2026"
    }
}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    msg = req.message.strip()

    if msg.startswith("SA-"):
        order = ORDERS.get(msg)
        if order:
            return {
                "reply": f"""✔ Đơn hàng {msg}
📦 Trạng thái: {order['status']}
🚚 Đơn vị: {order['carrier']}
📅 Dự kiến: {order['eta']}"""
            }
        return {"reply": "❌ Không tìm thấy đơn hàng."}

    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg}
        ],
        temperature=0.3
    )

    return {"reply": res.choices[0].message.content}
