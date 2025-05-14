import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import os
import ovh

from alias_manager import add_alias
from add_mxplan_account import add_mxplan_account
from your_config_loader import load_config

st.set_page_config(page_title="OVH MXPLAN / Email Pro / Exchange Dashboard", layout="wide")
st.title("📊 OVH Dashboard: MXPLAN, Email Pro, Exchange")

# Ścieżki
current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(current_dir, '..', '..', 'ovh_accounts.json'))
BASE_OUTPUT_DIR = os.path.join(current_dir, 'output')

# Wczytaj konfigurację
try:
    config = load_config(CONFIG_PATH)
    account_list = config['accounts']
except Exception as e:
    st.error(f"❌ Nie udało się wczytać pliku konfiguracyjnego: {e}")
    st.stop()

if not os.path.exists(BASE_OUTPUT_DIR):
    os.makedirs(BASE_OUTPUT_DIR)
    st.warning("⚠ Folder 'output' został utworzony, ale nie zawiera jeszcze danych. Uruchom najpierw main.py.")
    st.stop()

def get_run_folders():
    return sorted(
        [f for f in os.listdir(BASE_OUTPUT_DIR) if f.startswith('run_') and os.path.isdir(os.path.join(BASE_OUTPUT_DIR, f))],
        reverse=True
    )

def get_latest_file(folder_path, extension):
    files = [f for f in os.listdir(folder_path) if f.endswith(extension)]
    return os.path.join(folder_path, max(files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))) if files else None

# 📂 Wybór raportu
run_folders = get_run_folders()
if not run_folders:
    st.error("❌ Brak katalogów raportów. Uruchom main.py, aby wygenerować dane.")
    st.stop()

selected_run = st.selectbox("📂 Wybierz raport:", run_folders)
selected_folder_path = os.path.join(BASE_OUTPUT_DIR, selected_run)
st.info(f"📁 Wybrany folder: {selected_folder_path}")

csv_path = get_latest_file(selected_folder_path, '.csv')
if not csv_path:
    st.error(f"❌ Brak pliku CSV w {selected_folder_path}.")
    st.stop()

df = pd.read_csv(csv_path)
st.success(f"✅ Wczytano plik: {os.path.basename(csv_path)}")

# 🔍 Filtry
if 'type' in df.columns:
    types = ["All"] + sorted(df['type'].dropna().unique())
    selected_type = st.selectbox("Filtruj po typie usługi:", types)
    df = df if selected_type == "All" else df[df['type'] == selected_type]

offers = ["All"] + sorted(df['offer'].dropna().unique())
selected_offer = st.selectbox("Filtruj po pakiecie:", offers)
filtered_df = df if selected_offer == "All" else df[df['offer'] == selected_offer]

# 📋 Tabela skrzynek
st.write("### 📋 Tabela skrzynek e-mail (jeden wiersz = jedna skrzynka lub przekierowanie)")
columns_to_show = ['service', 'email', 'offer']
if 'type' in filtered_df.columns:
    columns_to_show.append('type')
if 'is_dmarc' in filtered_df.columns:
    columns_to_show.append('is_dmarc')
st.dataframe(filtered_df[columns_to_show])

# 📊 Wykresy – konta i przekierowania
if 'service' in filtered_df.columns and 'is_dmarc' in filtered_df.columns:

    st.write("### 📊 Liczba kont e-mail w serwisach")
    konta_df = filtered_df[filtered_df['is_dmarc'] != 'yes']
    if not konta_df.empty:
        konta_grouped = konta_df.groupby(['service', 'offer']).size().reset_index(name='count')
        konta_grouped['label'] = konta_grouped['service'] + '\n' + konta_grouped['offer']
        fig1, ax1 = plt.subplots(figsize=(max(12, len(konta_grouped) * 0.4), 6))
        ax1.bar(konta_grouped['label'], konta_grouped['count'], color='lightblue')
        ax1.set_xticks(range(len(konta_grouped['label'])))
        ax1.set_xticklabels(konta_grouped['label'], rotation=90, fontsize=8)
        ax1.set_ylabel("Liczba kont")
        ax1.set_title('Liczba kont przypisanych do serwisów')
        plt.tight_layout()
        st.pyplot(fig1)
    else:
        st.info("Brak kont e-mail do wyświetlenia.")

    st.write("### 📊 Liczba przekierowań w serwisach")
    fwd_df = filtered_df[filtered_df['is_dmarc'] == 'yes']
    if not fwd_df.empty:
        fwd_grouped = fwd_df.groupby(['service', 'offer']).size().reset_index(name='count')
        fwd_grouped['label'] = fwd_grouped['service'] + '\n' + fwd_grouped['offer']
        fig2, ax2 = plt.subplots(figsize=(max(12, len(fwd_grouped) * 0.4), 6))
        ax2.bar(fwd_grouped['label'], fwd_grouped['count'], color='lightgreen')
        ax2.set_xticks(range(len(fwd_grouped['label'])))
        ax2.set_xticklabels(fwd_grouped['label'], rotation=90, fontsize=8)
        ax2.set_ylabel("Liczba przekierowań")
        ax2.set_title('Liczba przekierowań (aliasów) w serwisach')
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.info("Brak przekierowań (aliasów) do wyświetlenia.")

else:
    st.warning("⚠ Brak kolumny 'service' lub 'is_dmarc' do wykresu.")

# 📥 Pobierz CSV
csv_download = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Pobierz cały raport jako CSV", csv_download, file_name=f"filtered_{os.path.basename(csv_path)}", mime='text/csv')

# 🌐 Graf interaktywny
html_graph_path = get_latest_file(selected_folder_path, '.html')
if html_graph_path:
    st.write("### 🌐 Interaktywny graf kont i przekierowań")
    with open(html_graph_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=900, scrolling=True)
else:
    st.warning("⚠ Brak wygenerowanego interaktywnego grafu w tym folderze.")

# ➕ Dodaj alias
st.write("### ➕ Dodaj alias (przekierowanie) do konta")
with st.form("add_alias_form"):
    selected_account_idx = st.selectbox("Konto OVH:", range(len(account_list)), format_func=lambda i: account_list[i]['name'])
    domain = st.text_input("Domena (np. example.com)", "")
    account = st.text_input("Konto docelowe (bez @domena)", "")
    new_alias = st.text_input("Adres aliasu (bez @domena)", "")
    if st.form_submit_button("Dodaj alias"):
        if not all([domain.strip(), account.strip(), new_alias.strip()]):
            st.error("❌ Uzupełnij wszystkie pola.")
        else:
            try:
                acc = account_list[selected_account_idx]
                client = ovh.Client(
                    endpoint='ovh-eu',
                    application_key=acc['application_key'],
                    application_secret=acc['application_secret'],
                    consumer_key=acc['consumer_key']
                )
                if add_alias(client, domain.strip(), account.strip(), new_alias.strip()):
                    st.success(f"✅ Przekierowanie {new_alias}@{domain} ➔ {account}@{domain} zostało dodane.")
                else:
                    st.error("❌ Nie udało się dodać przekierowania.")
            except Exception as e:
                st.error(f"❌ Błąd: {e}")

# ✉️ Dodaj konto
st.write("### ✉️ Dodaj nowe konto e-mail (MXPLAN)")
with st.form("add_mxplan_account_form"):
    selected_account_idx = st.selectbox("Konto OVH (MXPLAN):", range(len(account_list)), format_func=lambda i: account_list[i]['name'], key="mxplan_select")
    domain = st.text_input("Domena (np. example.com)", key="mxplan_domain")
    new_account = st.text_input("Nazwa konta (bez @)", key="mxplan_account")
    password = st.text_input("Hasło do konta", type="password", key="mxplan_password")
    quota = st.number_input("Quota (GB)", min_value=1, max_value=50, value=2, key="mxplan_quota")
    if st.form_submit_button("➕ Dodaj konto e-mail"):
        if not all([domain.strip(), new_account.strip(), password.strip()]):
            st.error("❌ Uzupełnij wszystkie pola.")
        else:
            try:
                acc = account_list[selected_account_idx]
                client = ovh.Client(
                    endpoint='ovh-eu',
                    application_key=acc['application_key'],
                    application_secret=acc['application_secret'],
                    consumer_key=acc['consumer_key']
                )
                if add_mxplan_account(client, domain.strip(), new_account.strip(), password.strip(), quota):
                    st.success(f"✅ Konto {new_account}@{domain} zostało utworzone.")
                else:
                    st.error("❌ Nie udało się utworzyć konta.")
            except Exception as e:
                st.error(f"❌ Błąd przy dodawaniu konta: {e}")
