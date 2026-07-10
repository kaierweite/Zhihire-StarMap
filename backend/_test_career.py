import httpx, json

# 先登录拿到 token
resp = httpx.post(
    'http://localhost:8000/api/auth/login',
    data={'username': 'test', 'password': 'test123'}
)
print('Login:', resp.status_code)
login_data = resp.json()
token = login_data.get('data', {}).get('access_token', '')
if not token:
    print('Login failed, trying userinfo...')
    print(json.dumps(login_data, indent=2, ensure_ascii=False)[:300])
else:
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test POST generate
    resp2 = httpx.post(
        'http://localhost:8000/api/career/plan/generate',
        json={'target_role_id': 1},
        headers=headers
    )
    print('\nPOST /plan/generate:', resp2.status_code)
    data = resp2.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:800])
    
    # Test GET plan
    resp3 = httpx.get('http://localhost:8000/api/career/plan', headers=headers)
    print('\nGET /plan:', resp3.status_code)
    print(json.dumps(resp3.json(), indent=2, ensure_ascii=False)[:500])
