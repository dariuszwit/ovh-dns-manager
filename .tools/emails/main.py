import json
import ovh
import logging
import os
import argparse
import subprocess
from datetime import datetime
from graph_drawer import build_interactive_graph
from static_graph import build_static_graph
from package_checker import check_account_packages
from summary_writer import save_email_summary
from generate_pdf_report import generate_pdf_report

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ścieżki główne
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', 'ovh_accounts.json'))
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')
NOTES_FILE = os.path.join(SCRIPT_DIR, 'notes.txt')  # opcjonalne notatki

os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def select_account(accounts, preselected_index=None):
    if preselected_index:
        if 1 <= preselected_index <= len(accounts):
            account = accounts[preselected_index - 1]
            logging.info(f"✅ Wybrano konto: {account['name']}")
            return account
        else:
            raise ValueError(f"❌ Nieprawidłowy numer konta: {preselected_index}")

    print("📂 Lista kont OVH:")
    for idx, acc in enumerate(accounts):
        print(f"{idx + 1}: {acc['name']}")
    while True:
        try:
            choice = int(input("🔢 Podaj numer konta do analizy: "))
            if 1 <= choice <= len(accounts):
                return accounts[choice - 1]
            else:
                print("❗ Spróbuj ponownie.")
        except ValueError:
            print("❗ Wprowadź poprawny numer.")

def create_client(account):
    logging.info(f"🔐 Tworzę klienta OVH dla: {account['name']}")
    return ovh.Client(
        endpoint='ovh-eu',
        application_key=account['application_key'],
        application_secret=account['application_secret'],
        consumer_key=account['consumer_key'],
    )

def main():
    parser = argparse.ArgumentParser(description="📧 OVH Email Scanner")
    parser.add_argument('--account', type=int, help='Numer konta do analizy (1, 2, ...)')
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)
    account = select_account(config['accounts'], args.account)
    client = create_client(account)

    # Katalog wyjściowy: run_<timestamp>
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_output_dir = os.path.join(BASE_OUTPUT_DIR, f'run_{timestamp}')
    os.makedirs(run_output_dir, exist_ok=True)

    # Ścieżki plików
    summary_file = os.path.join(run_output_dir, 'email_summary.txt')
    html_graph_file = os.path.join(run_output_dir, 'email_graph.html')
    png_graph_file = os.path.join(run_output_dir, 'email_graph.png')
    package_txt = os.path.join(run_output_dir, 'account_packages.txt')
    package_csv = os.path.join(run_output_dir, 'account_packages.csv')
    package_xlsx = os.path.join(run_output_dir, 'account_packages.xlsx')
    chart_accounts = os.path.join(run_output_dir, 'chart_accounts.png')
    chart_forwardings = os.path.join(run_output_dir, 'chart_forwardings.png')
    pdf_file = os.path.join(run_output_dir, 'final_report.pdf')

    # 🔍 Analiza
    all_data = check_account_packages(
        client,
        output_txt=package_txt,
        output_csv=package_csv,
        output_xlsx=package_xlsx,
        output_chart_accounts=chart_accounts,
        output_chart_forwardings=chart_forwardings,
        notes_file=NOTES_FILE
    )

    # 📄 Zapisywanie wyników
    save_email_summary(all_data, summary_file)
    build_interactive_graph(all_data, html_graph_file)
    build_static_graph(all_data, png_graph_file)

    generate_pdf_report(
        txt_summary=package_txt,
        graph_image=png_graph_file,
        chart_accounts=chart_accounts,
        chart_forwardings=chart_forwardings,
        output_pdf=pdf_file,
        notes_file=NOTES_FILE
    )

    # ✅ Podsumowanie
    print("\n🎉 Raporty zostały wygenerowane:")
    print(f"📄 Podsumowanie: {summary_file}")
    print(f"📄 TXT: {package_txt}")
    print(f"📄 CSV: {package_csv}")
    print(f"📄 XLSX: {package_xlsx}")
    print(f"📊 Wykres kont: {chart_accounts}")
    print(f"📊 Wykres przekierowań: {chart_forwardings}")
    print(f"🖼️ Graf PNG: {png_graph_file}")
    print(f"🌐 Graf HTML: {html_graph_file}")
    print(f"📑 PDF raport: {pdf_file}")
    print("\n🚀 Uruchamianie Streamlit dashboard...")

    try:
        subprocess.Popen([
            "python", "-m", "streamlit", "run", "dashboard.py", "--", "--output_dir", run_output_dir
        ])
    except Exception as e:
        logging.error(f"❌ Błąd przy uruchamianiu Streamlit: {e}")

if __name__ == '__main__':
    main()
