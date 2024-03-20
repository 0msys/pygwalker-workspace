from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st
import sqlite3


# dfかspecが変更された場合のみに再レンダリングするために、キャッシュを設定
@st.cache_data
def get_pyg_renderer(
    df: pd.DataFrame, spec: str = "./gw_config.json"
) -> "StreamlitRenderer":
    return StreamlitRenderer(df, spec=spec)


def save_dashboard(params: dict):
    """
    ダッシュボードの保存UIを表示する
    """

    st.sidebar.divider()

    st.sidebar.header("ダッシュボードの保存")

    # 保存する情報を入力。入力欄にはセッションから取得した値を初期値として設定
    save_category = st.sidebar.text_input(
        "カテゴリ名を入力してください", value=st.session_state.category
    )
    save_dashboard_name = st.sidebar.text_input(
        "ダッシュボード名を入力してください", value=st.session_state.dashboard_name
    )
    save_discription = st.sidebar.text_area(
        "ダッシュボードの説明を入力してください", value=st.session_state.discription
    )
    save_spec = st.sidebar.text_area("Exportしたspecを貼り付けてください")
    save_template = st.session_state.template

    # save_specの文頭にあるvis_spec = r"""と、文末にある"""を削除する
    save_spec = save_spec.replace('vis_spec = r"""', "").replace('"""', "")

    # dbに保存するために、paramsを文字列に変換
    save_params = str(params)

    # 必要項目が入力されたら保存ボタンを表示
    if save_category and save_dashboard_name and save_spec:

        if st.sidebar.button("保存"):
            conn = sqlite3.connect("db/dashboard.db")
            c = conn.cursor()

            # テーブルがなければ作成
            c.execute(
                "CREATE TABLE IF NOT EXISTS t_dashboard_list (category TEXT, dashboard_name TEXT, discription TEXT, spec TEXT, template TEXT, params TEXT)"
            )

            # 保存済みのダッシュボード(同カテゴリ・同名のダッシュボード)かどうかを確認
            c.execute(
                "SELECT * FROM t_dashboard_list WHERE category=? AND dashboard_name=?",
                (save_category, save_dashboard_name),
            )
            result = c.fetchone()
            if result:

                # 保存済みの場合は更新
                c.execute(
                    "UPDATE t_dashboard_list SET discription=?, spec=?, template=?, params=? WHERE category=? AND dashboard_name=?",
                    (
                        save_discription,
                        save_spec,
                        save_template,
                        save_params,
                        save_category,
                        save_dashboard_name,
                    ),
                )
                st.sidebar.write("更新しました")

            else:
                # 保存済みでない場合は新規保存
                c.execute(
                    "INSERT INTO t_dashboard_list VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        save_category,
                        save_dashboard_name,
                        save_discription,
                        save_spec,
                        save_template,
                        save_params,
                    ),
                )
                st.sidebar.write("保存しました")
            conn.commit()
            conn.close()
