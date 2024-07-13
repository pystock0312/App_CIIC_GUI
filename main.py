import pandas as pd
import streamlit as st
import os
import base64


# ログインセッションの状態管理
if 'login' not in st.session_state:
    st.session_state['login'] = False

# ログイン情報
correct_username = "user"
correct_password = "password"

# ログインフォーム
if not st.session_state['login']:
    with st.container():
        st.title("ログイン")
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        
        if st.button("ログイン"):
            if username == correct_username and password == correct_password:
                st.session_state['login'] = True
                st.success("ログイン成功")
                # ログイン成功後、ログインフォームを非表示にする
                st.experimental_rerun()
            else:
                st.error("ユーザー名またはパスワードが間違っています。")

# ログインが成功した場合の処理
if st.session_state['login']:
# ここにアプリケーションのメインコンテンツを配置
    # CSVファイルのパス
    csv_file_path = 'CIIC_data.csv'

    # CSVファイルをDataFrameとして読み込む
    df = pd.read_csv(csv_file_path)
    df = df.dropna(subset=['page_number'])
    df = df[['許可番号','会社名', '売上高', '経常利益', 'Y点', 'ISO9001登録', 'ISO14001登録','代表者名', '住所']]

    # 売上高列のデータを数値型に変換（変換できない値はNaNになる）
    df['売上高'] = pd.to_numeric(df['売上高'].str.replace(',', ''), errors='coerce')
    df['売上高'] = pd.to_numeric(df['売上高'], errors='coerce')
    df['経常利益'] = pd.to_numeric(df['経常利益'].str.replace(',', ''), errors='coerce')
    df['経常利益'] = pd.to_numeric(df['経常利益'], errors='coerce')
    # df['Y点'] = pd.to_numeric(df['Y点'].str.replace(',', ''), errors='coerce')
    # df['Y点'] = pd.to_numeric(df['Y点'], errors='coerce')


    df.astype({'売上高': int, '経常利益': int, 'Y点': int})

    # NaN値を0に置き換える（必要に応じて他の処理を行う）
    df['売上高'].fillna(0, inplace=True)
    df['経常利益'].fillna(0, inplace=True)
    df['Y点'].fillna(0, inplace=True)

    # 売上高の最小値と最大値を取得
    min_sales_value = int(df['売上高'].min())
    max_sales_value = int(df['売上高'].max())
    min_profit_value = int(df['経常利益'].min())
    max_profit_value = int(df['経常利益'].max())
    min_Y_value = int(df['Y点'].min())
    max_Y_value = int(df['Y点'].max())

    selected_min_sales_value, selected_max_sales_value = st.sidebar.slider('売上高の範囲,（円）', min_sales_value, max_sales_value, (min_sales_value, max_sales_value))
    selected_min_profit_value, selected_max_profit_value = st.sidebar.slider('経常利益の範囲,（円）', min_profit_value, max_profit_value, (min_profit_value, max_profit_value))
    selected_min_Y_value, selected_max_Y_value = st.sidebar.slider('Y点の範囲', min_Y_value, max_Y_value, (min_Y_value, max_Y_value))
    options_9001 = st.sidebar.multiselect('ISO9001登録', df['ISO9001登録'].unique(),default=df['ISO9001登録'].unique())
    options_14001 = st.sidebar.multiselect('ISO14001登録', df['ISO14001登録'].unique(),default=df['ISO14001登録'].unique())


    # # 選択された範囲でDataFrameをフィルタリング
    filtered_df = df[df['売上高'].between(selected_min_sales_value, selected_max_sales_value) & df['経常利益'].between(selected_min_profit_value, selected_max_profit_value) & df['Y点'].between(selected_min_Y_value, selected_max_Y_value) & df['ISO9001登録'].isin(options_9001) & df['ISO14001登録'].isin(options_14001)]
    # # フィルタリングされたDataFrameを表示
    st.dataframe(filtered_df)

    # マルチセレクトボックスで許可番号を選択
    selected_permit_numbers = st.multiselect(
        '許可番号を選択してください',
        options=filtered_df['許可番号'].unique()  # 許可番号の一覧を選択肢として設定
    )

    def show_pdf(file_path):
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    # 選択された許可番号に基づいてPDFファイルを検索し、表示
    pdf_directory = 'PDF_Files'
    for permit_number in selected_permit_numbers:
        pdf_file_path = os.path.join(pdf_directory, f'{permit_number}.pdf')
        if os.path.exists(pdf_file_path):
            show_pdf(pdf_file_path)
        else:
            st.write(f'{permit_number}に対応するPDFファイルが見つかりません。')


    pass