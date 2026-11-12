import urllib.request
import urllib.error
import json
import os

boundary = '----WebKitBoundary123'
lines = [
    '--' + boundary,
    'Content-Disposition: form-data; name="file"; filename="../../dangerous_traversal.txt"',
    'Content-Type: text/plain',
    '',
    'Confidential Security Directive text content for testing.',
    '--' + boundary + '--',
    ''
]
body = '\r\n'.join(lines).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8000/api/general-policy/v1/upload',
    data=body,
    headers={'Content-Type': 'multipart/form-data; boundary=' + boundary}
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print('[PASS] Response:', data)
    assert '..' not in data['filename']
    print(f"[PASS] Filename was sanitized safely to: '{data['filename']}'")
    
# Verify that no file was created outside uploads/
assert not os.path.exists(r'd:\Projects\Axiom\dangerous_traversal.txt')
print('[PASS] Traversal blocked: No file was written outside uploads/ directory.')
