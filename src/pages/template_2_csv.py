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
# PyGWalkerに渡すdfを作成

# 2つのデータをアップロードできるようにする
uploaded_file1 = st.sidebar.file_uploader(
    "1つ目のCSVファイルをアップロード", type="csv"
)
uploaded_file2 = st.sidebar.file_uploader(
    "2つ目のCSVファイルをアップロード", type="csv"
)

# ファイルがアップロードされた場合、データを読み込む
if uploaded_file1 is not None and uploaded_file2 is not None:
    df1 = pd.read_csv(uploaded_file1)
    df2 = pd.read_csv(uploaded_file2)

    columns1 = df1.columns
    columns2 = df2.columns

    # default_indexの初期化
    related_column_default_index1 = 0
    related_column_default_index2 = 0
    how_default_index = 0

    # テンプレートモードでない場合、セッションからデフォルトのindex値を取得
    if not st.session_state.template_mode:
        related_column_default_index1 = columns1.get_loc(
            st.session_state.params["related_column1"]
        )
        related_column_default_index2 = columns2.get_loc(
            st.session_state.params["related_column2"]
        )
        how_default_index = ["inner", "left", "right", "outer"].index(
            st.session_state.params["how"]
        )

    # ファイルのカラムからリレーションを掛けるカラムを選択
    related_column1 = st.sidebar.selectbox(
        "1つ目のファイルのカラムからリレーションを掛けるカラムを選択してください",
        columns1,
        index=related_column_default_index1,
    )
    related_column2 = st.sidebar.selectbox(
        "2つ目のファイルのカラムからリレーションを掛けるカラムを選択してください",
        columns2,
        index=related_column_default_index2,
    )

    # マージ方法を選択
    how = st.sidebar.selectbox(
        "マージ方法を選択してください",
        ["inner", "left", "right", "outer"],
        index=how_default_index,
    )

    # 指定された条件でマージ
    df = pd.merge(df1, df2, how=how, left_on=related_column1, right_on=related_column2)

    # ==============================================

    renderer = get_pyg_renderer(df, spec)

    # データ探索インターフェースをレンダリングする。
    renderer.render_explore()

    # ダッシュボードの保存UIを表示
    st.session_state.params = {
        "related_column1": related_column1,
        "related_column2": related_column2,
        "how": how,
    }
    save_dashboard(st.session_state.params)
