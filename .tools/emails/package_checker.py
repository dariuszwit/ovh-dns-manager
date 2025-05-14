import logging
import csv
import os
import collections
import matplotlib.pyplot as plt

try:
    import pandas as pd
except ImportError:
    pd = None


def check_account_packages(client, output_txt, output_csv=None, output_xlsx=None,
                           output_chart_accounts=None, output_chart_forwardings=None, notes_file=None):
    logging.info("🔍 Rozpoczynam analizę: MXPLAN, Email Pro, Exchange")

    all_data = {}
    rows = []
    package_counts = collections.Counter()

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("=== RAPORT KONFIGURACJI E-MAIL ===\n\n")

        # MXPLAN
        try:
            domains = client.get('/email/domain')
            for domain in domains:
                all_data.update(process_mxplan(client, domain, package_counts, rows, f))
        except Exception as e:
            logging.error(f"Błąd przy pobieraniu MXPLAN: {e}")

        # Email Pro
        try:
            pro_services = client.get('/email/pro')
            for service in pro_services:
                all_data.update(process_emailpro(client, service, package_counts, rows, f))
        except Exception as e:
            logging.error(f"Błąd przy pobieraniu Email Pro: {e}")

        # Exchange
        try:
            exchange_orgs = client.get('/email/exchange')
            for org in exchange_orgs:
                services = client.get(f'/email/exchange/{org}/service')
                for service in services:
                    all_data.update(process_exchange(client, org, service, package_counts, rows, f))
        except Exception as e:
            logging.error(f"Błąd przy pobieraniu Exchange: {e}")

        f.write("\n=== PODSUMOWANIE ===\n")
        for offer, count in package_counts.items():
            f.write(f"{offer}: {count} serwis(ów)\n")

    logging.info(f"📄 Raport TXT zapisany do {output_txt}")

    save_to_csv_and_excel(rows, output_csv, output_xlsx)

    if rows:
        if output_chart_accounts:
            plot_chart(rows, output_chart_accounts, count_type='accounts')
        if output_chart_forwardings:
            plot_chart(rows, output_chart_forwardings, count_type='forwardings')

    return all_data


def process_mxplan(client, domain, package_counts, rows, f):
    data = {}
    try:
        domain_info = client.get(f'/email/domain/{domain}')
        offer = domain_info.get('offer', 'MXPLAN')
        quota = domain_info.get('quota', 0)
        accounts = client.get(f'/email/domain/{domain}/account')

        f.write(f"=== MXPLAN - {domain} ===\n")
        f.write(f"Pakiet: {offer}, Maks: {quota}\n")

        emails = [f"{acc}@{domain}" for acc in accounts]
        forwardings = get_forwardings_for_domain(client, domain)

        for email in emails:
            rows.append(make_row("MXPLAN", domain, offer, email, quota, False))

        for fwd in forwardings:
            is_dmarc = fwd['from'].lower().startswith('_dmarc')
            rows.append(make_row("MXPLAN", domain, offer, fwd['from'], quota, is_dmarc))

        package_counts[offer] += 1
        data[domain] = {
            'accounts': emails,
            'forwardings': forwardings
        }

    except Exception as e:
        logging.error(f"Błąd MXPLAN {domain}: {e}")
    return data


def process_emailpro(client, service, package_counts, rows, f):
    data = {}
    try:
        info = client.get(f'/email/pro/{service}')
        offer = info.get('offer', 'EMAIL PRO')
        max_acc = info.get('maxAccount', 0)
        accounts = client.get(f'/email/pro/{service}/account')

        f.write(f"=== EMAIL PRO - {service} ===\n")
        f.write(f"Pakiet: {offer}, Maks: {max_acc}\n")

        emails = []
        for acc in accounts:
            email = acc['primaryEmailAddress']
            emails.append(email)
            rows.append(make_row("EMAIL PRO", service, offer, email, max_acc, False))
            f.write(f"  - {email}\n")

        package_counts[offer] += 1
        data[service] = {
            'accounts': emails,
            'forwardings': []
        }
    except Exception as e:
        logging.error(f"Błąd Email Pro {service}: {e}")
    return data


def process_exchange(client, org, service, package_counts, rows, f):
    data = {}
    try:
        info = client.get(f'/email/exchange/{org}/service/{service}')
        offer = info.get('offer', 'EXCHANGE')
        max_acc = info.get('maxAccount', 0)
        accounts = client.get(f'/email/exchange/{org}/service/{service}/account')

        f.write(f"=== EXCHANGE - {service} ===\n")
        f.write(f"Pakiet: {offer}, Maks: {max_acc}\n")

        emails = []
        for acc in accounts:
            email = acc['primaryEmailAddress']
            emails.append(email)
            rows.append(make_row("EXCHANGE", service, offer, email, max_acc, False))
            f.write(f"  - {email}\n")

        package_counts[offer] += 1
        data[service] = {
            'accounts': emails,
            'forwardings': []
        }
    except Exception as e:
        logging.error(f"Błąd Exchange {service}: {e}")
    return data


def get_forwardings_for_domain(client, domain):
    forwardings = []
    try:
        fwd_ids = client.get(f'/email/domain/{domain}/redirection')
        for fwd_id in fwd_ids:
            try:
                fwd = client.get(f'/email/domain/{domain}/redirection/{fwd_id}')
                forwardings.append({'from': fwd.get('from'), 'to': fwd.get('to')})
            except Exception as e:
                logging.warning(f"Błąd przekierowania {fwd_id} dla {domain}: {e}")
    except Exception as e:
        if '404' in str(e) or 'invalid (or empty) URL' in str(e):
            logging.info(f"Brak endpointu redirection dla {domain}")
        else:
            logging.warning(f"Błąd listy przekierowań dla {domain}: {e}")
    return forwardings


def make_row(typ, service, offer, email, max_acc, is_dmarc):
    return {
        'type': typ,
        'service': service,
        'offer': offer,
        'email': email,
        'max_accounts': max_acc,
        'is_dmarc': 'yes' if is_dmarc else ''
    }


def save_to_csv_and_excel(rows, output_csv, output_xlsx):
    if output_csv:
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['type', 'service', 'offer', 'email', 'max_accounts', 'is_dmarc']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
            logging.info(f"📄 Raport CSV zapisany do {output_csv}")
        except Exception as e:
            logging.error(f"Błąd CSV: {e}")

    if output_xlsx and pd:
        try:
            df = pd.DataFrame(rows)
            df.to_excel(output_xlsx, index=False)
            logging.info(f"📄 Raport Excel zapisany do {output_xlsx}")
        except Exception as e:
            logging.error(f"Błąd Excel: {e}")


def plot_chart(rows, output_chart, count_type='accounts'):
    try:
        counts = collections.Counter()
        offers = {}

        for row in rows:
            service = row['service']
            offer = row['offer']
            email = row['email']
            is_dmarc = row['is_dmarc'] == 'yes'

            # Rozpoznanie typu danych
            if '@' not in email:
                continue  # pomiń niepoprawne

            is_forwarding = is_dmarc or email.lower().startswith('_dmarc') or email.lower().startswith('dmarc')

            if (count_type == 'accounts' and not is_forwarding) or (count_type == 'forwardings' and is_forwarding):
                counts[service] += 1
                offers[service] = offer

        services = list(counts.keys())
        values = list(counts.values())

        fig_width = max(12, len(services) * 0.4)
        fig, ax = plt.subplots(figsize=(fig_width, 6))
        color = 'lightblue' if count_type == 'accounts' else 'lightgreen'
        bars = ax.bar(services, values, color=color)

        ax.set_xticks(range(len(services)))
        ax.set_xticklabels(services, rotation=90, fontsize=8)
        ax.set_ylabel("Liczba " + ("kont" if count_type == 'accounts' else "przekierowań"))
        ax.set_title("Liczba " + ("kont przypisanych do serwisów" if count_type == 'accounts' else "przekierowań (aliasów) w serwisach"))

        for i, bar in enumerate(bars):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    offers.get(services[i], ''), ha='center', va='bottom', fontsize=8, rotation=90)

        plt.tight_layout()
        plt.savefig(output_chart, bbox_inches='tight')
        plt.close()
        logging.info(f"📊 Wykres zapisany do {output_chart}")

    except Exception as e:
        logging.error(f"Błąd wykresu: {e}")

