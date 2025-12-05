import streamlit as st
import pandas as pd
import google.generativeai as genai 
import json
from datetime import datetime
import calendar
import random
from io import BytesIO

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="🔮 ดูดวง กับแม่หมอสมดุ๋ย",
    page_icon="🔮",
    layout="wide"
)

# ----------------------------
# Sidebar: API Key
# ----------------------------
st.sidebar.header("🔐 ตั้งค่า API Key")
gemini_api_key = st.sidebar.text_input("ใส่ Google Gemini API Key", type="password")

api_configured = False

if gemini_api_key:
    st.sidebar.success("✅ API Key ถูกตั้งค่าแล้ว")
    api_configured = True
else:
    st.sidebar.warning("⚠️ กรุณาใส่ API Key เพื่อใช้งาน")

st.sidebar.markdown("---")
st.sidebar.info("🔗 รับ API Key ได้ที่: [Google AI Studio](https://aistudio.google.com/app/apikey)")

# ----------------------------
# UI Layout
# ----------------------------
st.title("🔮 ดูดวง กับแม่หมอสมดุ๋ย")
st.write("กรอกข้อมูลส่วนตัวของคุณเพื่อรับคำทำนายแบบ personalize")

# --- Basic info form ---
col1, col2, col3 = st.columns(3)
with col1:
    first_name = st.text_input("ชื่อ *", placeholder="ระบุชื่อ")
with col2:
    last_name = st.text_input("นามสกุล *", placeholder="ระบุนามสกุล")
with col3:
    birthdate = st.date_input("วันเกิด *", min_value=datetime(1900, 1, 1))

col4, col5, col6 = st.columns(3)
with col4:
    birth_time = st.text_input("เวลาเกิด", placeholder="เช่น 08:30 (ไม่จำเป็น)")
with col5:
    gender = st.selectbox("เพศ", ["หญิง", "ชาย", "อื่น ๆ"])
with col6:
    location = st.text_input("สถานที่เกิด / ที่อยู่ปัจจุบัน", placeholder="เช่น กรุงเทพฯ")

st.markdown("---")

# ----------------------------
# สร้าง Calendar และ Random Fortune
# ----------------------------
def create_calendar():
    """สร้างปฏิทินเดือนปัจจุบัน"""
    now = datetime.now()
    year = now.year
    month = now.month
    today = now.day
    
    # สร้าง calendar
    cal = calendar.monthcalendar(year, month)
    month_name_th = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", 
        "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
        "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    
    # HTML Calendar
    html = f"""
    <style>
    .calendar {{
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}
    .calendar-header {{
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }}
    .calendar-grid {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        text-align: center;
    }}
    .day-header {{
        font-weight: bold;
        padding: 10px;
        background: rgba(255,255,255,0.2);
        border-radius: 8px;
    }}
    .day {{
        padding: 12px;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        transition: all 0.3s;
    }}
    .day:hover {{
        background: rgba(255,255,255,0.3);
        transform: scale(1.1);
    }}
    .today {{
        background: #FFD700 !important;
        color: #333 !important;
        font-weight: bold;
        box-shadow: 0 0 20px rgba(255,215,0,0.8);
    }}
    .empty {{
        background: transparent;
    }}
    </style>
    
    <div class="calendar">
        <div class="calendar-header">
            📅 {month_name_th[month-1]} {year + 543}
        </div>
        <div class="calendar-grid">
            <div class="day-header">อา</div>
            <div class="day-header">จ</div>
            <div class="day-header">อ</div>
            <div class="day-header">พ</div>
            <div class="day-header">พฤ</div>
            <div class="day-header">ศ</div>
            <div class="day-header">ส</div>
    """
    
    for week in cal:
        for day in week:
            if day == 0:
                html += '<div class="day empty"></div>'
            elif day == today:
                html += f'<div class="day today">{day}</div>'
            else:
                html += f'<div class="day">{day}</div>'
    
    html += """
        </div>
    </div>
    """
    return html

def generate_daily_fortune():
    """สุ่มโชครายวัน"""
    categories = [
        {"name": "ความรัก", "icon": "❤️", "color": "#FF6B6B"},
        {"name": "การงาน", "icon": "💼", "color": "#4ECDC4"},
        {"name": "การเงิน", "icon": "💰", "color": "#FFD93D"},
        {"name": "สุขภาพ", "icon": "🏥", "color": "#95E1D3"},
        {"name": "โชคลาภ", "icon": "🍀", "color": "#A8E6CF"}
    ]
    
    # สุ่ม 3 หมวดหมู่
    selected = random.sample(categories, 3)
    
    html = """
    <style>
    .fortune-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .fortune-header {
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .fortune-item {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s;
    }
    .fortune-item:hover {
        background: rgba(255,255,255,0.3);
        transform: translateX(10px);
    }
    .fortune-label {
        font-size: 18px;
        font-weight: bold;
    }
    .fortune-percent {
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    
    <div class="fortune-container">
        <div class="fortune-header">🔮 โชครายวันของคุณ</div>
    """
    
    for item in selected:
        percent = random.randint(60, 95)
        html += f"""
        <div class="fortune-item">
            <span class="fortune-label">{item['icon']} {item['name']}</span>
            <span class="fortune-percent">{percent}%</span>
        </div>
        """
    
    html += "</div>"
    return html

# ----------------------------
# Daily Fortune + Monthly Calendar
# ----------------------------
colA, colB = st.columns(2)
with colA:
    st.subheader("🔮 โชครายวันเป็นไงบ้าง")
    st.components.v1.html(generate_daily_fortune(), height=300)

with colB:
    st.subheader("📅 ปฏิทินรายเดือน")
    st.components.v1.html(create_calendar(), height=520)

st.markdown("---")

# ----------------------------
# User Question + AI Answer
# ----------------------------
prompt = st.text_input(
    "💭 คุณอยากถามเรื่องอะไรกับ AI หมอดู?", 
    placeholder="เช่น จะเจอเนื้อคู่เมื่อไหร่? จะสอบผ่านไหม? โชคการงานเป็นอย่างไร?"
)
ask_button = st.button("🔮 ทำนายเลย!", type="primary", use_container_width=True)

# ----------------------------
# ✅ เปลี่ยนเป็น Python SDK แทน REST API
# ----------------------------
def ask_gemini_sdk(prompt_text, api_key):
    """เรียก Gemini API ผ่าน Python SDK (เหมือนโค้ดแรก)"""
    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-09-2025",
        )
        
        response = model.generate_content(prompt_text)
        return response.text
        
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}"

# ----------------------------
# Logic when button clicked
# ----------------------------
if ask_button:
    
    if not api_configured:
        st.error("❌ กรุณาใส่ API Key ที่ Sidebar ด้านซ้ายก่อนใช้งาน")
        st.info("💡 **วิธีการ:** ไปที่ [Google AI Studio](https://aistudio.google.com/app/apikey) → สร้าง API Key → Copy มาวางในช่อง API Key")
        st.stop()
    
    if not first_name or not last_name:
        st.error("❌ กรุณากรอกชื่อ-นามสกุลให้ครบถ้วน")
        st.stop()
    
    if not prompt.strip():
        st.error("❌ กรุณาพิมพ์คำถามที่ต้องการถามหมอดู")
        st.stop()

    with st.spinner("🔮 กำลังทำนาย... กรุณารอสักครู่"):
        
        user_profile = (
            f"ชื่อ: {first_name} {last_name}\n"
            f"วันเกิด: {birthdate.strftime('%d/%m/%Y')}\n"
            f"เวลาเกิด: {birth_time if birth_time else 'ไม่ระบุ'}\n"
            f"เพศ: {gender}\n"
            f"สถานที่: {location if location else 'ไม่ระบุ'}\n"
        )

        full_prompt = f"""
        คุณคือหมอดู AI ผู้เชี่ยวชาญในการทำนายดวงส่วนบุคคล ชื่อ "แม่หมอสมดุ๋ย"
        
        ข้อมูลผู้ใช้:
        {user_profile}

        คำถามจากผู้ใช้:
        {prompt}

        กรุณาตอบเป็นภาษาไทย ให้ข้อมูลที่:
        1. เป็นมิตรและให้กำลังใจ
        2. ชัดเจนและเข้าใจง่าย
        3. มีคำแนะนำที่เป็นประโยชน์
        4. ยาวประมาณ 4-6 ประโยค
        """
        
        # ✅ เรียกใช้ฟังก์ชันใหม่แทน
        answer = ask_gemini_sdk(full_prompt, gemini_api_key)

    st.markdown("---")
    st.subheader("✨ คำตอบจากแม่หมอสมดุ๋ย")
    st.info(answer)

    # ----------------------------
    # ผลลัพธ์แบบ DataFrame + ดาวน์โหลด
    # ----------------------------
    st.markdown("---")
    st.subheader("📊 สรุปผลการทำนาย")
    
    df = pd.DataFrame({
        "หัวข้อ": [
            "ชื่อ-นามสกุล",
            "วันเกิด",
            "เวลาเกิด",
            "เพศ",
            "สถานที่",
            "คำถาม",
            "คำตอบ"
        ],
        "รายละเอียด": [
            f"{first_name} {last_name}",
            birthdate.strftime('%d/%m/%Y'),
            birth_time if birth_time else "ไม่ระบุ",
            gender,
            location if location else "ไม่ระบุ",
            prompt,
            answer
        ]
    })

    st.dataframe(df, use_container_width=True, height=350)

    # สร้างทั้ง CSV และ Excel
    csv = df.to_csv(index=False).encode('utf-8-sig')
    
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_data = excel_buffer.getvalue()
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        st.download_button(
            label="📥 ดาวน์โหลดเป็น CSV",
            data=csv,
            file_name=f"fortune_{first_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_dl2:
        st.download_button(
            label="📥 ดาวน์โหลดเป็น Excel",
            data=excel_data,
            file_name=f"fortune_{first_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.success("✅ ทำนายเสร็จสิ้น! สามารถดาวน์โหลดผลได้ด้านบน")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🔮 <b>ดูดวง กับแม่หมอสมดุ๋ย</b> | Powered by Google Gemini AI</p>
    <p style='font-size: 12px;'>⚠️ ผลการทำนายเพื่อความบันเทิงเท่านั้น ไม่ควรนำไปตัดสินใจเรื่องสำคัญ</p>
</div>

""", unsafe_allow_html=True)
