import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import io

# ===================== 1. 页面基础配置 =====================
st.set_page_config(
    page_title="船员生理要素智能手环监测",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ===================== 2. SessionState 全局状态初始化 =====================
if "is_login" not in st.session_state:
    st.session_state.is_login = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "current_menu" not in st.session_state:
    st.session_state.current_menu = "系统驾驶舱"
if "random_seed" not in st.session_state:
    st.session_state.random_seed = random.randint(1, 10000)

# ===================== 3. 全局CSS样式（重点修复下拉框截断 + 极限放大字体） =====================
st.markdown("""
<style>
    /* 隐藏默认元素，压缩留白 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {background-color: transparent;}
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 96% !important;}

    /* 1. 全局基础字体再次暴力放大 */
    html {font-size: clamp(20px, 1.8vw, 26px);} 
    body {
        font-size: inherit;
        line-height: 1.6;
        font-family: "Microsoft YaHei", "SimHei", "Segoe UI", Roboto, sans-serif;
        color: #e6f1ff;
        overflow-x: hidden; 
    }

    .stApp {
        background: linear-gradient(135deg, #0a192f 0%, #112240 100%);
        color: #e6f1ff;
    }

    /* 主标题极限放大 */
    .main-header {
        font-size: clamp(34px, 4vw, 46px); 
        font-weight: 800;
        background: linear-gradient(90deg, #00a8e8 0%, #64ffda 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0, 168, 232, 0.4);
    }
    .section-title {
        font-size: clamp(24px, 2.2vw, 30px);
        font-weight: 800;
        color: #ccd6f6;
        margin: 0.5rem 0;
        padding-left: clamp(10px, 1.2vw, 14px);
        border-left: 6px solid #64ffda;
    }

    /* 数据卡片 */
    .data-card {
        background: rgba(17, 34, 64, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 168, 232, 0.3);
        border-radius: clamp(8px, 1.5vw, 12px);
        padding: clamp(0.8rem, 1.5vw, 1.2rem); 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
        height: 100%;
        overflow: hidden;
    }
    .data-card:hover { border-color: rgba(0, 168, 232, 0.6); transform: translateY(-2px); }
    .card-label {
        font-size: clamp(20px, 1.8vw, 24px); /* 标签字号大幅放大 */
        color: #a8b2d1;
        margin-bottom: 0.3rem;
        font-weight: 700;
    }
    .card-value {
        font-size: clamp(42px, 4.5vw, 56px); /* 核心数字震撼放大 */
        font-weight: 800;
        color: #ccd6f6;
        line-height: 1.1;
        margin-bottom: 0.3rem;
    }
    .card-desc {
        font-size: clamp(16px, 1.4vw, 18px);
        color: #8892b0;
    }

    /* 状态标签放大 */
    .tag-success, .tag-warning, .tag-danger, .tag-info {
        padding: 6px 14px;
        border-radius: 6px;
        font-size: clamp(16px, 1.5vw, 18px);
        font-weight: 800;
        display: inline-block;
    }
    .tag-success {background: rgba(46, 204, 113, 0.15); color: #36e27f; border: 1px solid rgba(46, 204, 113, 0.5);}
    .tag-warning {background: rgba(243, 156, 18, 0.15); color: #f9b14a; border: 1px solid rgba(243, 156, 18, 0.5);}
    .tag-danger {background: rgba(231, 76, 60, 0.15); color: #f26457; border: 1px solid rgba(231, 76, 60, 0.5);}
    .tag-info {background: rgba(52, 152, 219, 0.15); color: #4ea8de; border: 1px solid rgba(52, 152, 219, 0.5);}

    /* 2. 表格字体显著放大 */
    .dataframe {
        width: 100%;
        border-collapse: collapse;
        background: rgba(17, 34, 64, 0.7);
        border-radius: 8px;
    }
    .dataframe th {
        background: linear-gradient(90deg, rgba(0, 119, 190, 0.3) 0%, rgba(0, 168, 232, 0.2) 100%);
        color: #64ffda;
        padding: 12px 16px;
        text-align: left;
        font-weight: 800;
        font-size: clamp(18px, 1.6vw, 22px); /* 表头字号极限放大 */
    }
    .dataframe td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(25, 42, 66, 0.9);
        color: #ccd6f6;
        font-size: clamp(18px, 1.6vw, 20px); /* 表格内容放大 */
        font-weight: 500;
    }
    .dataframe tbody tr:hover { background: rgba(0, 168, 232, 0.15); }
    .text-danger {color: #f26457; font-weight: 800;}
    .text-warning {color: #f9b14a; font-weight: 800;}
    .text-success {color: #36e27f; font-weight: 800;}

    /* 侧边栏字体放大 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a192f 0%, #051020 100%);
        border-right: 1px solid rgba(0, 168, 232, 0.3);
        min-width: clamp(280px, 26vw, 340px) !important; 
        max-width: clamp(280px, 26vw, 340px) !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        font-size: clamp(20px, 1.8vw, 24px); /* 侧边栏按钮文字放大 */
        font-weight: 800;
        padding: 16px 18px; 
        margin-bottom: 10px;
        background: transparent;
        color: #a8b2d1;
        border-radius: 8px;
        text-align: left;
        border-left: 4px solid transparent;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(0, 168, 232, 0.15);
        color: #ccd6f6;
        border-left: 4px solid rgba(0, 168, 232, 0.6);
    }
    [data-testid="stSidebar"] .stButton>button:focus:not(:active) {
        background: rgba(0, 168, 232, 0.2);
        color: #64ffda;
        font-weight: 800;
        border-left: 4px solid #64ffda;
    }

    /* 侧边栏卡片和头像放大 */
    .user-card {
        background: rgba(0, 168, 232, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 10px;
        display: flex;
        align-items: center;
        gap: 15px;
        border: 1px solid rgba(0, 168, 232, 0.2);
    }
    .user-avatar {
        width: 60px; height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00a8e8 0%, #64ffda 100%);
        color: #0a192f;
        display: flex; justify-content: center; align-items: center;
        font-weight: 800; font-size: 26px;
    }


    /* ================= 重点修复：下拉框和输入框被截断的致命Bug + 字体颜色 ================= */

    /* 1. 修复文本输入框（修改输入账号时的字体颜色） */
    .stTextInput input {
        background-color: rgba(17, 34, 64, 0.9) !important;
        border: 1px solid rgba(0, 168, 232, 0.4) !important;
        color: #64ffda !important; 
        font-size: clamp(20px, 1.8vw, 24px) !important; 
        font-weight: 800 !important; 
        border-radius: 8px !important;
        padding: 12px 15px !important; 
        min-height: 52px !important;   
    }
    
    /* 其他普通数字输入框保持浅白色 */
    .stNumberInput input {
        background-color: rgba(17, 34, 64, 0.9) !important;
        border: 1px solid rgba(0, 168, 232, 0.4) !important;
        color: #ffffff !important;
        font-size: clamp(20px, 1.8vw, 24px) !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        padding: 12px 15px !important; 
        min-height: 52px !important;  
    }

    /* 2. 修复下拉框 (Selectbox) 被压扁的问题及内部字体颜色 */
    div[data-baseweb="select"] > div {
        background-color: rgba(17, 34, 64, 0.9) !important;
        border: 1px solid rgba(0, 168, 232, 0.4) !important;
        border-radius: 8px !important;
        min-height: 54px !important; 
    }
    div[data-baseweb="select"] * {
        color: #ffffff !important; /* 强制下拉框及内部所有文字（如"全部"）为纯白 */
    }
    div[data-baseweb="select"] span {
        font-size: clamp(20px, 1.8vw, 24px) !important; 
        font-weight: 800 !important;
    }
    /* 修复下拉菜单弹出后的选项列表背景和字体看不清的问题 */
    ul[data-baseweb="menu"] li {
        background-color: #0a192f !important;
        color: #ffffff !important;
        font-size: 18px !important;
    }

    /* 3. 放大输入框/下拉框上方的标题文字 */
    .stTextInput>label, .stSelectbox>label, .stNumberInput>label {
        color: #64ffda !important; /* 统一改为高亮青色 */
        font-size: clamp(22px, 2vw, 26px) !important; 
        font-weight: 800 !important;
        padding-bottom: 8px !important;
    }


    /* 登录框样式 */
    [data-testid="stForm"] {
        background: rgba(17, 34, 64, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(0, 168, 232, 0.3) !important;
        border-radius: 15px !important;
        padding: 40px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
    }
    .login-title {
        text-align: center;
        font-size: clamp(30px, 3vw, 40px); /* 登录标题放大 */
        font-weight: 800;
        color: #64ffda;
        margin-bottom: 20px;
    }

    .js-plotly-plot .plotly { background: transparent !important; }
    [data-testid="stHorizontalBlock"] { gap: 1rem !important; }
    [data-testid="stMetric"] { padding: 0.5rem !important; }

    /* ================= 重点修复：二级界面（如张伟等基础信息）字体太浅的问题 ================= */
    [data-testid="stMetricLabel"] p {
        color: #64ffda !important; /* "船员姓名" 等标签改为高亮青色 */
        font-size: 18px !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricValue"] div {
        color: #ffffff !important; /* "张伟" 等具体数值改为纯白并加粗 */
        font-size: clamp(28px, 3vw, 36px) !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== 4. 基础配置 =====================
USER_CONFIG = {
    "admin": {"password": "123456", "name": "系统管理员", "role": "admin", "avatar": "管"},
    "crew": {"password": "123456", "name": "张伟", "show_name": "船员-张伟", "role": "crew", "crew_id": "CY2024001", "ship_name": "远洋01号", "avatar": "船"}
}

SHIP_LIST = ["远洋01号", "远洋02号", "远航03号", "中海05号", "长航08号"]
POST_LIST = ["船长", "大副", "二副", "轮机长", "轮机员", "甲板水手", "水手长", "船舶医生", "厨师", "电机员"]
WARNING_INDEX_LIST = [
    {"name": "心率", "unit": "次/分钟", "normal": "60-100次/分钟"},
    {"name": "血压(收缩压)", "unit": "mmHg", "normal": "90-140mmHg"},
    {"name": "血氧饱和度", "unit": "%", "normal": "95%-100%"},
    {"name": "体温", "unit": "℃", "normal": "36.0-37.2℃"},
    {"name": "睡眠时长", "unit": "小时", "normal": "≥6小时"},
]

FIRST_NAME = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "马", "胡"]
LAST_NAME = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "艳", "勇", "涛"]
def generate_name():
    return random.choice(FIRST_NAME) + random.choice(LAST_NAME)

def refresh_data():
    st.session_state.random_seed = random.randint(1, 10000)
    st.rerun()

def generate_crew_data():
    random.seed(st.session_state.random_seed)
    crew_list = []
    for i in range(25):
        # 强制保证第一条数据叫张伟，防止船员登录时报错
        name = "张伟" if i == 0 else generate_name()
        ship = random.choice(SHIP_LIST)
        age = random.randint(22, 55)
        crew_list.append({
            "crew_id": f"CY2024{i+1:03d}",
            "name": name,
            "ship_name": ship,
            "post": random.choice(POST_LIST),
            "age": age,
            "gender": random.choice(["男", "女"]),
            "work_age": random.randint(1, age-21),
            "device_id": f"SB2024{i+1:03d}",
            "heart_rate": random.randint(60, 100) if random.random() > 0.3 else random.randint(40, 140),
            "sbp": random.randint(90, 140) if random.random() > 0.3 else random.randint(80, 180),
            "dbp": random.randint(60, 90),
            "spo2": random.randint(95, 100) if random.random() > 0.2 else random.randint(85, 94),
            "temperature": round(random.uniform(36.0, 37.2), 1) if random.random() > 0.2 else round(random.uniform(37.3, 39.5), 1),
            "device_status": random.choice(["在线", "在线", "在线", "离线"]),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return crew_list

def generate_warning_data(crew_list):
    random.seed(st.session_state.random_seed)
    warning_list = []
    for i in range(80):
        crew = random.choice(crew_list)
        warning_index = random.choice(WARNING_INDEX_LIST)
        warning_level = random.randint(1, 3)
        handle_status = random.randint(0, 1)
        
        if warning_index["name"] == "心率":
            abnormal_value = f"{random.randint(101, 140) if warning_level >=2 else random.randint(40, 59)}次/分钟"
        elif warning_index["name"] == "血压(收缩压)":
            abnormal_value = f"{random.randint(141, 180)}mmHg"
        elif warning_index["name"] == "血氧饱和度":
            abnormal_value = f"{random.randint(85, 94)}%"
        elif warning_index["name"] == "体温":
            abnormal_value = f"{round(random.uniform(37.3, 39.5), 1)}℃"
        else:
            abnormal_value = f"{round(random.uniform(3, 5.9), 1)}小时"
        
        warning_list.append({
            "warning_id": f"YJ{datetime.now().strftime('%Y%m%d')}{i+1:03d}",
            "crew_name": crew["name"],
            "ship_name": crew["ship_name"],
            "abnormal_index": warning_index["name"],
            "abnormal_value": abnormal_value,
            "normal_range": warning_index["normal"],
            "warning_level": warning_level,
            "warning_time": (datetime.now() - timedelta(minutes=random.randint(1, 10080))).strftime("%Y-%m-%d %H:%M:%S"),
            "handle_status": handle_status,
            "handle_user": random.choice(["船舶医生-刘医生", "船舶管理员-王队", "系统管理员"]) if handle_status == 1 else "-"
        })
    return warning_list

def generate_device_data(crew_list):
    random.seed(st.session_state.random_seed)
    device_list = []
    for crew in crew_list:
        device_list.append({
            "device_id": crew["device_id"],
            "device_model": "HT-001Pro",
            "bind_crew": crew["name"],
            "ship_name": crew["ship_name"],
            "waterproof": "IP68",
            "battery_life": "正常模式7天",
            "device_status": crew["device_status"],
            "battery": random.randint(10, 100),
            "last_online": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if crew["device_status"] == "在线" else (datetime.now() - timedelta(minutes=random.randint(1, 1440))).strftime("%Y-%m-%d %H:%M:%S")
        })
    for i in range(60 - len(crew_list)):
        status = random.choice(["未启用", "未启用", "故障", "故障", "离线"])
        device_list.append({
            "device_id": f"SB2024{len(crew_list)+i+1:03d}",
            "device_model": "HT-001Pro",
            "bind_crew": "未绑定",
            "ship_name": random.choice(["仓库备用", "返厂维修"] + SHIP_LIST),
            "waterproof": "IP68",
            "battery_life": "正常模式7天",
            "device_status": status,
            "battery": random.randint(0, 100) if status != "故障" else 0,
            "last_online": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d %H:%M:%S") if status != "未启用" else "-"
        })
    return device_list

def generate_crew_trend_data(crew_info):
    random.seed(st.session_state.random_seed + hash(crew_info["crew_id"]))
    day_list = [f"{i+1}日" for i in range(30)]
    base_heart = 75 if crew_info["age"] < 40 else 80
    base_bp = 120 if crew_info["age"] < 40 else 130
    base_spo2 = 98
    heart_data = [base_heart + random.randint(-10, 15) for _ in range(30)]
    bp_data = [base_bp + random.randint(-10, 20) for _ in range(30)]
    spo2_data = [base_spo2 + random.randint(-2, 1) for _ in range(30)]
    return day_list, heart_data, bp_data, spo2_data

def get_warning_tag(level):
    if level == 3: return '<span class="tag-danger">重度预警</span>'
    elif level == 2: return '<span class="tag-warning">中度预警</span>'
    else: return '<span class="tag-warning">轻度预警</span>'

def get_handle_tag(status):
    if status == 0: return '<span class="tag-danger">未处理</span>'
    else: return '<span class="tag-success">已处理</span>'

def get_device_tag(status):
    if status == "在线": return '<span class="tag-success">在线</span>'
    elif status == "离线": return '<span class="tag-warning">离线</span>'
    elif status == "故障": return '<span class="tag-danger">故障</span>'
    else: return '<span class="tag-info">未启用</span>'

def highlight_heart_rate(x):
    if x > 100 or x < 60: return f'<span class="text-danger">{x}</span>'
    return f'<span class="text-success">{x}</span>'

def highlight_spo2(x):
    if x < 95: return f'<span class="text-warning">{x}</span>'
    return f'<span class="text-success">{x}</span>'

def highlight_temperature(x):
    if x > 37.2 or x < 35: return f'<span class="text-warning">{x}</span>'
    return f'<span class="text-success">{x}</span>'

def highlight_bp(x):
    if x > 140 or x < 90: return f'<span class="text-danger">{x}</span>'
    return f'<span class="text-success">{x}</span>'

def highlight_battery(x):
    if x < 20: return f'<span class="text-danger">{x}%</span>'
    return f'<span class="text-success">{x}%</span>'

def login_check(username, password):
    username = username.strip()
    password = password.strip()
    user = USER_CONFIG.get(username)
    if user and user["password"] == password:
        st.session_state.is_login = True
        st.session_state.user_info = user
        st.session_state.current_menu = "系统驾驶舱"
        st.rerun()
    else:
        st.error("账号或密码错误，请重新输入")

def logout():
    st.session_state.is_login = False
    st.session_state.user_info = {}
    st.session_state.current_menu = "系统驾驶舱"
    st.rerun()

# ===================== 6. 业务页面模块 =====================
def dashboard_page(crew_list, warning_list, device_list):
    st.markdown('<div class="main-header">船员生理要素智能手环监测 · 全局系统驾驶舱</div>', unsafe_allow_html=True)
    
    col_btn1, _, _ = st.columns([1, 1, 8])
    with col_btn1:
        if st.button("🔄 刷新实时数据", type="primary", use_container_width=True):
            refresh_data()

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        online_crew = len([x for x in crew_list if x["device_status"] == "在线"])
        online_rate = round(online_crew / len(crew_list) * 100, 1)
        st.markdown(f"""
        <div class="data-card">
            <div class="card-label">在船船员总数</div>
            <div class="card-value">{len(crew_list)}</div>
            <div class="card-desc">在线率 {online_rate}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        online_device = len([x for x in device_list if x["device_status"] == "在线"])
        device_online_rate = round(online_device / len(device_list) * 100, 1)
        st.markdown(f"""
        <div class="data-card">
            <div class="card-label">手环设备总数</div>
            <div class="card-value">{len(device_list)}</div>
            <div class="card-desc">在线率 {device_online_rate}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        untreated_warning = len([x for x in warning_list if x["handle_status"] == 0])
        st.markdown(f"""
        <div class="data-card">
            <div class="card-label">今日预警总数</div>
            <div class="card-value">{len(warning_list)}</div>
            <div class="card-desc">未处理 {untreated_warning} 条</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        high_risk = len([x for x in warning_list if x["warning_level"] == 3])
        st.markdown(f"""
        <div class="data-card">
            <div class="card-label">高风险人员</div>
            <div class="card-value">{high_risk}</div>
            <div class="card-desc">较昨日 +{random.randint(0, 3)}</div>
        </div>
        """, unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns([1, 2], gap="medium")
    with chart_col1:
        st.markdown('<div class="data-card"><div class="section-title">预警分级统计</div></div>', unsafe_allow_html=True)
        warning_count = [
            len([x for x in warning_list if x["warning_level"] == 1]),
            len([x for x in warning_list if x["warning_level"] == 2]),
            len([x for x in warning_list if x["warning_level"] == 3])
        ]
        warning_labels = ["轻度预警", "中度预警", "重度预警"]
        warning_colors = ["#f9b14a", "#e67e22", "#f26457"]
        
        if sum(warning_count) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=warning_labels, values=warning_count, hole=0.4,
                marker=dict(colors=warning_colors, line=dict(color='#0a192f', width=2)),
                textfont=dict(color='#ccd6f6', size=16)
            )])
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccd6f6', size=16),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=0, b=0, l=0, r=0), height=220
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown('<div class="data-card"><div class="section-title">24小时生理异常趋势</div></div>', unsafe_allow_html=True)
        hour_list = [f"{i}时" for i in range(24)]
        heart_rate_data = [random.randint(0, 6) for _ in range(24)]
        bp_data = [random.randint(0, 4) for _ in range(24)]
        spo2_data = [random.randint(0, 2) for _ in range(24)]
        temp_data = [random.randint(0, 1) for _ in range(24)]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=hour_list, y=heart_rate_data, mode='lines', name='心率异常', line=dict(color='#64ffda', width=3)))
        fig_line.add_trace(go.Scatter(x=hour_list, y=bp_data, mode='lines', name='血压异常', line=dict(color='#f26457', width=3)))
        fig_line.add_trace(go.Scatter(x=hour_list, y=spo2_data, mode='lines', name='血氧异常', line=dict(color='#36e27f', width=3)))
        fig_line.add_trace(go.Scatter(x=hour_list, y=temp_data, mode='lines', name='体温异常', line=dict(color='#f9b14a', width=3)))
        
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccd6f6', size=16),
            legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="center", x=0.5), hovermode="x unified",
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'), yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='异常次数'),
            margin=dict(t=0, b=0, l=10, r=10), height=220
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown('<div class="data-card"><div class="section-title">实时异常预警列表</div></div>', unsafe_allow_html=True)
    if warning_list:
        warning_df = pd.DataFrame(warning_list[:5]) 
        warning_df["预警级别"] = warning_df["warning_level"].apply(lambda x: get_warning_tag(x))
        warning_df["处理状态"] = warning_df["handle_status"].apply(lambda x: get_handle_tag(x))
        warning_show_df = warning_df[["crew_name", "ship_name", "abnormal_index", "abnormal_value", "预警级别", "warning_time", "处理状态"]]
        warning_show_df.columns = ["船员姓名", "所属船舶", "异常指标", "异常数值", "预警级别", "预警时间", "处理状态"]
        st.markdown(warning_show_df.to_html(escape=False, index=False, classes="dataframe"), unsafe_allow_html=True)

# ========= 更新布局的 monitor_page =========
def monitor_page(crew_list):
    st.markdown('<div class="main-header">实时生理监测 · 多传感器数据采集</div>', unsafe_allow_html=True)
    user_role = st.session_state.user_info["role"]
    filter_data = crew_list.copy()
    
    if user_role == "crew":
        crew_name = st.session_state.user_info["name"]
        filter_data = [x for x in crew_list if x["name"] == crew_name]
        st.info(f"当前仅展示您（{st.session_state.user_info['show_name']}）的生理监测数据")

    # ========= 将原来的两列合并为一列，让按钮自动到下拉框下方 =========
    col1, _ = st.columns([2, 10], gap="medium") 
    with col1:
        if user_role == "admin":
            ship_list = ["全部"] + SHIP_LIST
            selected_ship = st.selectbox("选择船舶", ship_list)
            if selected_ship != "全部":
                filter_data = [x for x in filter_data if x["ship_name"] == selected_ship]
        
        # 给按钮增加10像素的顶部间距，防止和下拉框贴得太紧
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        
        if st.button("🔄 刷新实时数据", type="primary", use_container_width=True):
            refresh_data()
    # ========================================================================

    st.markdown('<div class="data-card"><div class="section-title">船员实时生理数据列表</div></div>', unsafe_allow_html=True)
    if filter_data:
        monitor_df = pd.DataFrame(filter_data[:8])  
        monitor_df["心率(次/分)"] = monitor_df["heart_rate"].apply(highlight_heart_rate)
        monitor_df["血压(mmHg)"] = monitor_df["sbp"].apply(highlight_bp)
        monitor_df["血氧饱和度(%)"] = monitor_df["spo2"].apply(highlight_spo2)
        monitor_df["体温(℃)"] = monitor_df["temperature"].apply(highlight_temperature)
        monitor_df["设备状态"] = monitor_df["device_status"].apply(get_device_tag)
        
        monitor_show_df = monitor_df[["name", "ship_name", "post", "心率(次/分)", "血压(mmHg)", "血氧饱和度(%)", "体温(℃)", "设备状态", "update_time"]]
        monitor_show_df.columns = ["船员姓名", "所属船舶", "岗位", "心率(次/分)", "血压(mmHg)", "血氧饱和度(%)", "体温(℃)", "设备状态", "更新时间"]
        st.markdown(monitor_show_df.to_html(escape=False, index=False, classes="dataframe"), unsafe_allow_html=True)
    
    st.markdown("### 生理指标趋势分析")
    trend_col1, trend_col2 = st.columns(2, gap="large")
    time_list = [f"{i}:00" for i in range(10, 18)]
    with trend_col1:
        st.markdown('<div class="data-card"><div class="section-title">心率实时趋势</div></div>', unsafe_allow_html=True)
        zs_heart = [random.randint(60, 100) for _ in range(7)]
        ls_heart = [random.randint(60, 100) for _ in range(7)]
        fig_heart = go.Figure()
        fig_heart.add_trace(go.Scatter(x=time_list, y=zs_heart, mode='lines+markers', name='船员1-心率', line=dict(color='#f26457', width=3), marker=dict(size=8)))
        fig_heart.add_trace(go.Scatter(x=time_list, y=ls_heart, mode='lines+markers', name='船员2-心率', line=dict(color='#64ffda', width=3), marker=dict(size=8)))
        fig_heart.add_hline(y=100, line_dash="dash", line_color="#f26457", annotation_text="上限", annotation_font_color="#f26457")
        fig_heart.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccd6f6', size=16), margin=dict(t=0,b=0,l=0,r=0), height=200)
        st.plotly_chart(fig_heart, use_container_width=True)

    with trend_col2:
        st.markdown('<div class="data-card"><div class="section-title">血氧饱和度实时趋势</div></div>', unsafe_allow_html=True)
        ls_spo2 = [random.randint(95, 100) for _ in range(7)]
        zs_spo2 = [random.randint(95, 100) for _ in range(7)]
        fig_spo2 = go.Figure()
        fig_spo2.add_trace(go.Scatter(x=time_list, y=ls_spo2, mode='lines+markers', name='船员1-血氧', line=dict(color='#f9b14a', width=3), marker=dict(size=8)))
        fig_spo2.add_trace(go.Scatter(x=time_list, y=zs_spo2, mode='lines+markers', name='船员2-血氧', line=dict(color='#36e27f', width=3), marker=dict(size=8)))
        fig_spo2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccd6f6', size=16), margin=dict(t=0,b=0,l=0,r=0), height=200)
        st.plotly_chart(fig_spo2, use_container_width=True)

def warning_page(warning_list):
    st.markdown('<div class="main-header">预警管理中心 · 三级分级预警机制</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        st.markdown(f'<div class="data-card"><div class="card-label">累计预警总数</div><div class="card-value">{len(warning_list) + 1200}</div><div class="card-desc">本月新增 300 条</div></div>', unsafe_allow_html=True)
    with col2:
        high_count = len([x for x in warning_list if x["warning_level"] == 3])
        st.markdown(f'<div class="data-card"><div class="card-label">重度预警</div><div class="card-value">{high_count + 125}</div><div class="card-desc">&nbsp;</div></div>', unsafe_allow_html=True)
    with col3:
        mid_count = len([x for x in warning_list if x["warning_level"] == 2])
        st.markdown(f'<div class="data-card"><div class="card-label">中度预警</div><div class="card-value">{mid_count + 450}</div><div class="card-desc">&nbsp;</div></div>', unsafe_allow_html=True)
    with col4:
        light_count = len([x for x in warning_list if x["warning_level"] == 1])
        st.markdown(f'<div class="data-card"><div class="card-label">轻度预警</div><div class="card-value">{light_count + 670}</div><div class="card-desc">&nbsp;</div></div>', unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3 = st.columns(3, gap="medium")
    with filter_col1: selected_level = st.selectbox("预警级别", ["全部", "轻度预警", "中度预警", "重度预警"])
    with filter_col2: selected_status = st.selectbox("处理状态", ["全部", "未处理", "已处理"])
    with filter_col3: selected_ship = st.selectbox("所属船舶", ["全部"] + SHIP_LIST)

    filter_warning = warning_list.copy()
    if selected_level != "全部":
        level_map = {"轻度预警":1, "中度预警":2, "重度预警":3}
        filter_warning = [x for x in filter_warning if x["warning_level"] == level_map[selected_level]]
    if selected_status != "全部":
        status_map = {"未处理":0, "已处理":1}
        filter_warning = [x for x in filter_warning if x["handle_status"] == status_map[selected_status]]
    if selected_ship != "全部":
        filter_warning = [x for x in filter_warning if x["ship_name"] == selected_ship]

    st.markdown('<div class="data-card"><div class="section-title">全量预警记录</div></div>', unsafe_allow_html=True)
    if filter_warning:
        warning_df = pd.DataFrame(filter_warning[:12])  
        warning_df["预警级别"] = warning_df["warning_level"].apply(lambda x: get_warning_tag(x))
        warning_df["处理状态"] = warning_df["handle_status"].apply(lambda x: get_handle_tag(x))
        warning_show_df = warning_df[["warning_id", "crew_name", "ship_name", "abnormal_index", "abnormal_value", "normal_range", "预警级别", "warning_time", "处理状态", "handle_user"]]
        warning_show_df.columns = ["预警ID", "船员姓名", "所属船舶", "异常指标", "异常数值", "正常范围", "预警级别", "预警时间", "处理状态", "处理人"]
        st.markdown(warning_show_df.to_html(escape=False, index=False, classes="dataframe"), unsafe_allow_html=True)

def crew_page(crew_list):
    st.markdown('<div class="main-header">船员健康档案 · 全周期健康管理</div>', unsafe_allow_html=True)
    user_role = st.session_state.user_info["role"]
    if user_role == "crew":
        crew_name = st.session_state.user_info["name"]
        selected_crew = crew_name
    else:
        crew_name_list = [x["name"] for x in crew_list]
        selected_crew = st.selectbox("选择船员", crew_name_list)
    
    # 强制安全获取信息
    crew_filter = [x for x in crew_list if x["name"] == selected_crew]
    crew_info = crew_filter[0] if crew_filter else crew_list[0]
    
    st.markdown('<div class="data-card"><div class="section-title">船员基础信息</div></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1: st.metric("船员姓名", crew_info["name"])
    with col2: st.metric("所属船舶", crew_info["ship_name"])
    with col3: st.metric("年龄", crew_info["age"])
    with col4: st.metric("工龄", f"{crew_info['work_age']}年")

    st.markdown('<div class="data-card"><div class="section-title">近30天生理指标趋势</div></div>', unsafe_allow_html=True)
    day_list, heart_data, bp_data, spo2_data = generate_crew_trend_data(crew_info)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=day_list, y=heart_data, name='平均心率(次/分)', line=dict(color='#00a8e8', width=3)))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccd6f6', size=16), margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig, use_container_width=True)

def device_page(device_list):
    st.markdown('<div class="main-header">设备管理中心 · 智能手环终端管理</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1: st.markdown(f'<div class="data-card"><div class="card-label">设备总数量</div><div class="card-value">{len(device_list)}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="data-card"><div class="card-label">在线设备</div><div class="card-value">{len([x for x in device_list if x["device_status"] == "在线"])}</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="data-card"><div class="card-label">离线设备</div><div class="card-value">{len([x for x in device_list if x["device_status"] == "离线"])}</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="data-card"><div class="card-label">故障设备</div><div class="card-value">{len([x for x in device_list if x["device_status"] == "故障"])}</div></div>', unsafe_allow_html=True)

    filter_device = device_list.copy()
    st.markdown('<div class="data-card"><div class="section-title">设备台账列表</div></div>', unsafe_allow_html=True)
    if filter_device:
        device_df = pd.DataFrame(filter_device[:15])  
        device_df["设备状态"] = device_df["device_status"].apply(get_device_tag)
        device_df["电量"] = device_df["battery"].apply(highlight_battery)
        
        device_show_df = device_df[["device_id", "device_model", "bind_crew", "ship_name", "waterproof", "battery_life", "设备状态", "电量", "last_online"]]
        device_show_df.columns = ["设备编号", "设备型号", "绑定船员", "所属船舶", "防水等级", "续航能力", "设备状态", "电量", "最后在线时间"]
        st.markdown(device_show_df.to_html(escape=False, index=False, classes="dataframe"), unsafe_allow_html=True)
        
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                device_show_df.to_excel(writer, sheet_name='设备台账', index=False)
            st.download_button(label="📊 导出当前设备台账Excel", data=output.getvalue(), file_name=f"设备台账_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
        except Exception: pass

def system_page():
    st.markdown('<div class="main-header">系统管理 · 平台配置中心</div>', unsafe_allow_html=True)
    if st.session_state.user_info["role"] != "admin":
        st.error("您无权限访问该模块，仅超级管理员可查看")
        return
    st.markdown('<div class="data-card"><div class="section-title">系统用户管理</div></div>', unsafe_allow_html=True)
    user_data = [
        {"user_id": "U001", "username": "admin", "name": "系统管理员", "role": "超级管理员", "org": "哈尔滨海泰新航电子", "status": "启用"},
        {"user_id": "U002", "username": "ship01", "name": "王队", "role": "船舶管理员", "org": "远洋01号", "status": "启用"},
    ]
    user_df = pd.DataFrame(user_data)
    user_df["账号状态"] = user_df["status"].apply(lambda x: '<span class="tag-success">启用</span>')
    st.markdown(user_df.to_html(escape=False, index=False, classes="dataframe"), unsafe_allow_html=True)

# ===================== 7. 登录页面 =====================
def login_page():
    st.markdown('<div style="margin-top: 15vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header" style="text-align: center; border: none;">船员生理要素智能手环监测</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #a8b2d1; font-size: clamp(20px, 2vw, 24px); margin-bottom: 40px;">综合监控云平台</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<div class="login-title">用户登录</div>', unsafe_allow_html=True)
            username = st.text_input("账号", placeholder="请输入账号：admin / crew")
            password = st.text_input("密码", type="password", placeholder="请输入密码：123456")
            st.markdown("<br>", unsafe_allow_html=True)
            login_btn = st.form_submit_button("登 录", type="primary", use_container_width=True)
            
            if login_btn:
                login_check(username, password)
        
        st.markdown("""
        <div style="text-align: center; color: #a8b2d1; font-size: 16px; margin-top: 20px;">
            管理员账号：admin 密码：123456<br>
            船员账号：crew 密码：123456
        </div>
        """, unsafe_allow_html=True)

# ===================== 8. 主程序入口 =====================
def main():
    if not st.session_state.is_login:
        login_page()
        return
    
    with st.sidebar:
        user_info = st.session_state.user_info
        st.markdown(f"""
        <div class="user-card">
            <div class="user-avatar">{user_info['avatar']}</div>
            <div>
                <div style="font-size: clamp(22px, 2vw, 26px); font-weight: 800; color: #ccd6f6;">{user_info['name']}</div>
                <div style="font-size: clamp(18px, 1.6vw, 20px); color: #a8b2d1;">{user_info['role'] == 'admin' and '系统管理员' or user_info['show_name']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        menu_list = [
            {"name": "系统驾驶舱", "icon": "📊"},
            {"name": "实时生理监测", "icon": "❤️"},
            {"name": "预警管理中心", "icon": "⚠️"},
            {"name": "船员健康档案", "icon": "👤"},
            {"name": "设备管理中心", "icon": "⌚"},
        ]
        if st.session_state.user_info["role"] == "admin":
            menu_list.append({"name": "系统管理", "icon": "⚙️"})
        
        for menu in menu_list:
            if st.button(f"{menu['icon']} {menu['name']}", use_container_width=True):
                st.session_state.current_menu = menu["name"]
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 退出登录", use_container_width=True): logout()
    
    CREW_DATA = generate_crew_data()
    WARNING_DATA = generate_warning_data(CREW_DATA)
    DEVICE_DATA = generate_device_data(CREW_DATA)
    
    current_menu = st.session_state.current_menu
    if current_menu == "系统驾驶舱": dashboard_page(CREW_DATA, WARNING_DATA, DEVICE_DATA)
    elif current_menu == "实时生理监测": monitor_page(CREW_DATA)
    elif current_menu == "预警管理中心": warning_page(WARNING_DATA)
    elif current_menu == "船员健康档案": crew_page(CREW_DATA)
    elif current_menu == "设备管理中心": device_page(DEVICE_DATA)
    elif current_menu == "系统管理": system_page()

if __name__ == "__main__":
    main()
