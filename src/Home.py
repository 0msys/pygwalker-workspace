import pandas as pd
import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="PyGWalker WorkSpace", layout="wide")

# 初期化
if "template_mode" not in st.session_state:
    st.session_state.template_mode = False
    st.session_state.category = ""
    st.session_state.dashboard_name = ""
    st.session_state.discription = ""
    st.session_state.spec = ""
    st.session_state.template = ""
    st.session_state.params = {}

# タイトルを表示
st.title("Home")

# 一緒に表示すると見づらいので、タブで分けて表示する
tab1, tab2 = st.tabs(["既存のダッシュボードを開く", "新規ダッシュボードを作成"])


with tab1:

    # dbの存在確認。なければ既存のダッシュボードはないので、何もしない
    if os.path.exists("db/dashboard.db"):

        # dbからダッシュボード情報を取得
        conn = sqlite3.connect("db/dashboard.db")
        dashboard_df = pd.read_sql("SELECT * FROM t_dashboard_list", conn)
        conn.close()

        if not dashboard_df.empty:

            # ダッシュボード一覧を表示
            with st.expander("ダッシュボード一覧", expanded=False):
                st.dataframe(dashboard_df, hide_index=True)

            # カテゴリーとダッシュボード名を選択
            categories = dashboard_df["category"].unique()
            category = st.selectbox("カテゴリー", categories)
            dashboard_name = st.selectbox(
                "ダッシュボード名",
                dashboard_df[dashboard_df["category"] == category][
                    "dashboard_name"
                ].unique(),
            )

            # 選択したダッシュボードの情報を取得
            discritption = dashboard_df[
                (dashboard_df["category"] == category)
                & (dashboard_df["dashboard_name"] == dashboard_name)
            ]["discription"].values[0]
            spec = dashboard_df[
                (dashboard_df["category"] == category)
                & (dashboard_df["dashboard_name"] == dashboard_name)
            ]["spec"].values[0]
            template = dashboard_df[
                (dashboard_df["category"] == category)
                & (dashboard_df["dashboard_name"] == dashboard_name)
            ]["template"].values[0]
            params = dashboard_df[
                (dashboard_df["category"] == category)
                & (dashboard_df["dashboard_name"] == dashboard_name)
            ]["params"].values[0]

            # paramsはdb内で文字列として保存されているので、辞書型に変換
            if params != "{}":
                params = dict(eval(params))
            else:
                params = {}

            # ダッシュボードの情報を表示
            st.caption(f"説明: {discritption}")
            st.caption(f"使用テンプレート: {template}")
            st.caption(f"パラメータ: {params}")

            # ダッシュボードを開くボタンと削除ボタンを並べて表示
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("ダッシュボードを開く"):

                    # 選択したダッシュボードの情報をセッションに保存して、指定のダッシュボード(templateページ)を開く
                    st.session_state.template_mode = False
                    st.session_state.category = category
                    st.session_state.dashboard_name = dashboard_name
                    st.session_state.discription = discritption
                    st.session_state.spec = spec
                    st.session_state.template = template
                    st.session_state.params = params

                    st.switch_page(f"pages/{template}")

            with col2:
                # 間違えて削除しないように、ポップオーバーで確認を取る
                popover = st.popover("ダッシュボードを削除")
                with popover:
                    st.markdown("本当に削除してよろしいですか？")
                    if st.button("削除"):
                        conn = sqlite3.connect("db/dashboard.db")
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM t_dashboard_list WHERE category=? AND dashboard_name=?",
                            (category, dashboard_name),
                        )
                        conn.commit()
                        conn.close()
                        st.success("削除しました")

with tab2:

    # pagesフォルダ内の.pyファイル一覧を取得(_で始まるファイルは除外)
    pages = os.listdir("src/pages")
    pages = [page for page in pages if page.endswith(".py")]
    pages = [page for page in pages if not page.startswith("_")]

    # 昇順にソート
    pages.sort()

    # 新規作成するダッシュボードのテンプレートを選択
    page = st.selectbox("作成するダッシュボードのテンプレートを選択", pages)

    if st.button("テンプレートを開く"):

        # ダッシュボードの情報を初期化して、テンプレートモードをTrueにして、ダッシュボード(templateページ)を開く
        st.session_state.template_mode = True
        st.session_state.category = ""
        st.session_state.dashboard_name = ""
        st.session_state.discription = ""
        st.session_state.spec = ""
        st.session_state.template = page
        st.session_state.params = {}

        st.switch_page(f"pages/{page}")
