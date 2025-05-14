import logging

def add_alias(client, domain, account, alias):
    """Dodaj alias do konta e-mail w OVH."""
    try:
        result = client.post(f'/email/domain/{domain}/account/{account}/alias', alias=alias)
        logging.info(f"✅ Alias {alias}@{domain} dodany do {account}@{domain}")
        return result
    except Exception as e:
        logging.error(f"❌ Błąd przy dodawaniu aliasu {alias}@{domain} do {account}@{domain}: {e}")
        return None
