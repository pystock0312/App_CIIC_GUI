import pandas as pd
import streamlit as st

# ログイン情報
correct_username = "user"
correct_password = "password"

# ログインフォーム
if 'login' not in st.session_state:
    st.session_state['login'] = False

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
    # csv_file_path = '20241012_00_08_09_10_11_12_13_14.csv'

    # # CSVファイルを読み込む
    # df = pd.read_csv(csv_file_path)
    # df = df.dropna(subset=['page_number'])

    # # pickleファイルに変換
    # df.to_pickle('df.pkl')
    # pickleファイルを読み込む
    df = pd.read_pickle('df.pkl')
    # フリガナ列は不要なので削除
    df = df.drop(columns=['フリガナ'])

    # # 住所列から都道府県を抽出
    # df['都道府県'] = df['住所'].str.extract(r'(\S{2,3}[都道県])')
    # df.to_pickle('df.pkl')
    # pickleファイルを読み込む

    # 売上高列のデータを数値型に変換（変換できない値はNaNになる）
    if df['売上高'].dtype != 'object':
        df['売上高'] = df['売上高'].astype(str)
    df['売上高'] = pd.to_numeric(df['売上高'].str.replace(',', ''), errors='coerce')

    if df['経常利益'].dtype != 'object':
        df['経常利益'] = df['経常利益'].astype(str)
    df['経常利益'] = pd.to_numeric(df['経常利益'].str.replace(',', ''), errors='coerce')

    if df['Y点'].dtype != 'object':
        df['Y点'] = df['Y点'].astype(str)
    df['Y点'] = pd.to_numeric(df['Y点'].str.replace(',', ''), errors='coerce')

    # NaN値をそのままにしておく
    # 列を整数型に変換
    df = df.astype({'売上高': 'Int64', '経常利益': 'Int64', 'Y点': 'Int64'})

    # 売上高の最小値と最大値を取得
    min_sales_value = int(df['売上高'].min()) if not pd.isna(df['売上高'].min()) else 0
    max_sales_value = int(df['売上高'].max()) if not pd.isna(df['売上高'].max()) else 0
    min_profit_value = int(df['経常利益'].min()) if not pd.isna(df['経常利益'].min()) else 0
    max_profit_value = int(df['経常利益'].max()) if not pd.isna(df['経常利益'].max()) else 0
    min_Y_value = int(df['Y点'].min()) if not pd.isna(df['Y点'].min()) else 0
    max_Y_value = int(df['Y点'].max()) if not pd.isna(df['Y点'].max()) else 0

    # サイドバーにスライダーを追加
    selected_min_sales_value, selected_max_sales_value = st.sidebar.slider('売上高の範囲（円）', min_sales_value, max_sales_value, (min_sales_value, max_sales_value))
    selected_min_profit_value, selected_max_profit_value = st.sidebar.slider('経常利益の範囲（円）', min_profit_value, max_profit_value, (min_profit_value, max_profit_value))
    selected_min_Y_value, selected_max_Y_value = st.sidebar.slider('Y点の範囲', min_Y_value, max_Y_value, (min_Y_value, max_Y_value))

    # マルチセレクトボックスを追加
    options_9001 = st.sidebar.multiselect('ISO9001登録', df['ISO9001登録'].unique(), default=df['ISO9001登録'].unique())
    options_14001 = st.sidebar.multiselect('ISO14001登録', df['ISO14001登録'].unique(), default=df['ISO14001登録'].unique())

    # 都道府県と市区町村のマルチセレクトボックス
    prefecture_options = st.sidebar.multiselect('都道府県', df['都道府県'].unique(), default=df['都道府県'].unique())
    # 選択された都道府県に紐づく市区町村を取得。デフォルトは全て選択された状態
    city_options = st.sidebar.multiselect('市町村', df[df['都道府県'].isin(prefecture_options)]['市町村名'].unique(), default=df[df['都道府県'].isin(prefecture_options)]['市町村名'].unique())


    # 会社名検索ボックス
    company_name_search = st.sidebar.text_input('会社名（全角・漢字）を検索')

    # フィルタリングされたDataFrameを表示
    filtered_df = df[
        (df['売上高'].between(selected_min_sales_value, selected_max_sales_value)) &
        (df['経常利益'].between(selected_min_profit_value, selected_max_profit_value)) &
        (df['Y点'].between(selected_min_Y_value, selected_max_Y_value)) &
        (df['ISO9001登録'].isin(options_9001)) &
        (df['ISO14001登録'].isin(options_14001)) &
        (df['都道府県'].isin(prefecture_options)) &
        (df['市町村名'].isin(city_options))
    ]

    # 会社名フィルタリング（全角の漢字を部分一致で検索）
    if company_name_search:
        filtered_df = filtered_df[filtered_df['会社名'].str.contains(company_name_search)]

    # テーブルデータを表示
    st.dataframe(filtered_df)
