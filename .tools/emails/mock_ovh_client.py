class MockOVHClient:
    def get(self, path):
        print(f"[MOCK GET] {path}")
        if path == '/email/domain':
            return ['example.com']
        if path.startswith('/email/domain/example.com'):
            if path.endswith('/account'):
                return ['kontakt', 'biuro', 'info']
            if '/alias' in path:
                return ['alias1', 'alias2']
            return {'offer': 'MXPLAN 5', 'quota': 5}
        if path == '/email/pro':
            return ['pro-service']
        if path.startswith('/email/pro/pro-service'):
            if path.endswith('/account'):
                return [{'primaryEmailAddress': 'user@pro.com'}, {'primaryEmailAddress': 'admin@pro.com'}]
            return {'offer': 'EMAIL PRO', 'maxAccount': 10}
        if path == '/email/exchange':
            return ['exchange-org']
        if path.startswith('/email/exchange/exchange-org/service'):
            if path.endswith('/account'):
                return [{'primaryEmailAddress': 'john@exchange.com'}, {'primaryEmailAddress': 'jane@exchange.com'}]
            return ['exchange-service']
        return []

    def post(self, path, **kwargs):
        print(f"[MOCK POST] {path} with {kwargs}")
        return {'success': True}
