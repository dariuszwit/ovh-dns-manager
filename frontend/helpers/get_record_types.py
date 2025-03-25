from frontend.constants.dns_record_types import DNS_RECORD_TYPES

def get_record_types():
    """ Zwraca pełną listę obsługiwanych typów rekordów DNS """
    print(f"✅ Returning full list of supported record types: {DNS_RECORD_TYPES}")
    return DNS_RECORD_TYPES
