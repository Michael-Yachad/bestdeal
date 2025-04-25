
import streamlit as st
import xmltodict
import pandas as pd
import os
import json

FAV_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def fetch_prices_from_file(file_path="products.xml"):
    with open(file_path, 'r', encoding='utf-8') as xml_file:
        return xmltodict.parse(xml_file.read())

def get_product_image_local(product_name):
    product_name = product_name.lower()
    if "חלב" in product_name:
        return "images/milk.jpg"
    elif "לחם" in product_name:
        return "images/bread.jpg"
    elif "גבינה" in product_name:
        return "images/cheese.jpg"
    else:
        return "images/default.jpg"

def display_prices(data_dict):
    st.set_page_config(page_title="BestDeal", layout="centered")
    st.title("🛒 BestDeal - עוזר הקניות שלך")

    products = data_dict['Prices']['Products']['Product']
    df = pd.DataFrame(products)
    df['ItemPrice'] = pd.to_numeric(df['ItemPrice'], errors='coerce')

    if 'favorites' not in st.session_state:
        st.session_state.favorites = load_favorites()

    tab1, tab2 = st.tabs(["🛍 כל המוצרים", "⭐ המועדפים שלי"])

    with tab1:
        st.subheader("🔍 חיפוש ומיון")
        search_query = st.text_input("חפש מוצר לפי שם:")
        sort_order = st.radio("מיין לפי מחיר:", ("⬆️ מהזול ליקר", "⬇️ מהיקר לזול"))

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df['ItemName'].str.contains(search_query, case=False, na=False)]
        filtered_df = filtered_df.sort_values(by='ItemPrice', ascending=(sort_order == "⬆️ מהזול ליקר"))

        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.image(get_product_image_local(row['ItemName']), width=80)
                    st.write(f"**{row['ItemName']}** – {row['ItemPrice']} ₪")
                with col2:
                    if st.button("💙", key=f"fav_{row['ItemName']}"):
                        if row['ItemName'] not in st.session_state.favorites:
                            st.session_state.favorites.append(row['ItemName'])
                            save_favorites(st.session_state.favorites)
        else:
            st.info("לא נמצאו מוצרים.")

    with tab2:
        st.subheader("⭐ המועדפים שלי")
        if st.session_state.favorites:
            fav_df = df[df['ItemName'].isin(st.session_state.favorites)]

            for _, row in fav_df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.image(get_product_image_local(row['ItemName']), width=80)
                    st.write(f"✅ **{row['ItemName']}** – {row['ItemPrice']} ₪")
                with col2:
                    if st.button("🗑️", key=f"remove_{row['ItemName']}"):
                        st.session_state.favorites.remove(row['ItemName'])
                        save_favorites(st.session_state.favorites)
                        st.rerun()

            csv = fav_df[['ItemName', 'ItemPrice']].rename(columns={
                'ItemName': 'שם מוצר',
                'ItemPrice': 'מחיר (₪)'
            }).to_csv(index=False).encode('utf-8-sig')

            st.download_button(
                label="📥 הורד מועדפים כ־CSV",
                data=csv,
                file_name="bestdeal_favorites.csv",
                mime='text/csv'
            )
        else:
            st.info("לא נוספו מועדפים.")

if __name__ == "__main__":
    try:
        data_dict = fetch_prices_from_file()
        display_prices(data_dict)
    except Exception as e:
        st.error(f"שגיאה: {e}")
