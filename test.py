import urllib.request, json

data = json.dumps({"regions": ["apac", "amer"], "threshold_ms": 151}).encode()
req = urllib.request.Request(
    "https://iitm-ga-0.vercel.app/analytics",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
response = urllib.request.urlopen(req)
print(json.loads(response.read().decode()))