import logging

def save_email_summary(all_data, output_file):
    """Zapisuje zbiorcze i szczegółowe dane o skrzynkach i przekierowaniach do pliku tekstowego."""

    all_accounts_set = set()
    all_forwardings_list = []

    # Zbierz wszystkie adresy i przekierowania
    for service, data in all_data.items():
        accounts = data.get('accounts', [])
        forwardings = data.get('forwardings', [])

        for acc in accounts:
            all_accounts_set.add(acc)

        for fwd in forwardings:
            pair = f"{fwd.get('from')} → {fwd.get('to')}"
            all_forwardings_list.append(pair)

    # Zapisz do pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        # Podsumowanie globalne
        f.write("=== PODSUMOWANIE GLOBALNE ===\n")
        f.write(f"🧾 Łączna liczba unikalnych skrzynek: {len(all_accounts_set)}\n")
        for email in sorted(all_accounts_set):
            f.write(f" - {email}\n")

        f.write(f"\n🔁 Łączna liczba przekierowań: {len(all_forwardings_list)}\n")
        for pair in sorted(all_forwardings_list):
            f.write(f" - {pair}\n")

        # Szczegóły per usługa
        for service, data in all_data.items():
            f.write(f"\n=== Usługa: {service} ===\n")

            # Skrzynki
            f.write("📨 Skrzynki:\n")
            if data.get('accounts'):
                for acc in data['accounts']:
                    f.write(f" - {acc}\n")
            else:
                f.write(" (brak skrzynek)\n")

            # Przekierowania
            f.write("🔁 Przekierowania:\n")
            if data.get('forwardings'):
                for fwd in data['forwardings']:
                    from_ = fwd.get('from')
                    to_ = fwd.get('to')
                    if from_ and to_:
                        f.write(f" - {from_} → {to_}\n")
            else:
                f.write(" (brak przekierowań)\n")

    logging.info(f"📄 Email summary saved to {output_file}")
