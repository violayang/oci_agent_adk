# app_text2image.py
import json
import requests
import streamlit as st

st.set_page_config(page_title="Text_2_Image Agent", page_icon="🖼", layout="wide")
st.markdown("Search :material/settings: for options.")
st.title("🖼️ ERP - Text_2_Image Agent")
st.caption("Uploads an image and a question, calls /query/image, and displays the agent's answer.")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("🔧 Configuration")
    base_url = st.text_input("Base URL", value="http://localhost:8084/", help="Root of your API (no trailing slash)")
    base_url = base_url.rstrip('/')
    timeout = st.number_input("HTTP Timeout (s)", value=60, min_value=1, max_value=600)
    st.markdown("---")
    st.subheader("Run server")
    st.code("streamlit run app_text2image.py --server.address 0.0.0.0 --server.port 8084")

session = requests.Session()

def _url(path: str) -> str:
    return f"{base_url}{path if path.startswith('/') else '/' + path}"

def POST(path, **kw):
    return session.post(_url(path), timeout=timeout, **kw)

# ---------------- Tool UI ----------------
st.subheader("🛠️ Tool")
st.caption("Wired to your endpoint: /query/image")

col1 = st.columns(1)[0]
with col1:
    st.markdown("**Text_2_Image — Agent**")
    q_question = st.text_input("question", value="Get all information about the order", key="q1")
    q_image = st.file_uploader("image", type=["png", "jpg", "jpeg"], key="f1")

st.markdown("---")

# ---------------- Simple Diagram (LangGraph-like) ----------------
diagram_placeholder = st.empty()

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_SUCCESS = "success"
STATUS_FAIL = "fail"

def render_graph(status_map):
    colors = {
        STATUS_PENDING: "#e5e7eb",
        STATUS_RUNNING: "#fde68a",
        STATUS_SUCCESS: "#bbf7d0",
        STATUS_FAIL: "#fecaca",
    }
    dot = []
    dot.append('digraph G {')
    dot.append('rankdir="LR";')
    dot.append('node [fontname="Helvetica"];')
    dot.append('A [label="Master Agent \\n OrderX Hub", shape="circle", style="filled", fillcolor="#e0e7ff"];')
    stt = status_map.get("T1", STATUS_PENDING)
    dot.append(f'T1 [label="Text_2_Image\\n Agent", shape="box", style="filled,rounded", fillcolor="{colors[stt]}"];')
    dot.append("A -> T1;")
    dot.append("}")
    diagram_placeholder.graphviz_chart("\n".join(dot))

status_map = {"T1": STATUS_PENDING}
render_graph(status_map)

# ---------------- Logs + Execute ----------------
run_col, log_col = st.columns([1, 2])
with run_col:
    run = st.button("🚀 Execute Text_2_Image Agent")

with log_col:
    st.markdown("**Live Logs**")
    log_area = st.empty()

def stream_log(line=None, reset=False):
    if reset or "log_lines" not in st.session_state:
        st.session_state["log_lines"] = []
    if line is not None:
        st.session_state["log_lines"].append(line)
    content = "\n".join(st.session_state["log_lines"][-500:])
    log_area.code(content)

def show_payload(title, payload):
    st.markdown(f"**{title}**")
    if isinstance(payload, (dict, list)):
        st.json(payload)
    else:
        st.code(str(payload)[:5000])

if run:
    stream_log(reset=True)

    # Validate input
    if q_image is None:
        stream_log("Please upload an image before running.")
    else:
        # Step 1: Text_2_Image
        status_map["T1"] = STATUS_RUNNING
        render_graph(status_map)
        stream_log("Step 1: Text_2_Image — uploading image + question…")

        try:
            files = {"image": (q_image.name, q_image.getvalue(), q_image.type or "image/jpeg")}
            data = {"question": q_question}
            r1 = POST("/query/image", files=files, data=data, headers={"accept": "application/json"})

            try:
                p1 = r1.json() if r1.headers.get("content-type", "").startswith("application/json") else r1.text
            except Exception:
                p1 = r1.text

            ok1 = r1.ok
            stream_log(f"Step 1 → HTTP {r1.status_code}")
            status_map["T1"] = STATUS_SUCCESS if ok1 else STATUS_FAIL
            render_graph(status_map)
            show_payload("/query/image response", p1)

            if not ok1:
                stream_log("Step 1 failed.")
        except Exception as e:
            status_map["T1"] = STATUS_FAIL
            render_graph(status_map)
            stream_log(f"Step 1 error: {e}")

    stream_log("Done.")
