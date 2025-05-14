def add_mxplan_account(client, domain, account_name, password, quota):
    try:
        result = client.post(
            f'/email/domain/{domain}/account',
            accountName=account_name,
            password=password,
            quota=quota
        )
        return result
    except Exception as e:
        print(f"Błąd przy tworzeniu konta MXPLAN: {e}")
        return None
