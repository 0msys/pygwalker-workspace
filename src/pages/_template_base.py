from pygwalker.api.streamlit import init_streamlit_comm
import pandas as pd
import streamlit as st

from utils import get_pyg_renderer, save_dashboard


st.set_page_config(page_title="PyGWalker WorkSpace", layout="wide")

# Homeに戻るリンクを追加
st.sidebar.page_link(page="Home.py", label="Homeに戻る")

# PyGWalkerとStreamlitの通信を確立する
init_streamlit_comm()

if st.session_state.template_mode:
    # テンプレートモードの場合、specをデフォルトに設定する
    spec = "./gw_config.json"

else:
    # テンプレートモードでない場合、specをセッションから取得し、使い方を表示する
    spec = st.session_state.spec
    st.markdown(f"### 使い方\n\n{st.session_state.discription}")


# ==============================================
# ここにPyGWalkerに渡すdfを作成するコードを記述する。


# ==============================================

renderer = get_pyg_renderer(df, spec)

# データ探索インターフェースをレンダリングする。
renderer.render_explore()

# ダッシュボードの保存UIを表示
# ダッシュボードの表示に必要なパラメータが有れば、それをdbに保存する
st.session_state.params = {
    "param1": param1,
    "param2": param2,
    "param3": param3,
}
save_dashboard(st.session_state.params)
