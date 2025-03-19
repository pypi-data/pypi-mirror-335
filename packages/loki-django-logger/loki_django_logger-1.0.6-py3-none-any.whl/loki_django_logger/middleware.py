# middleware.py
from django.utils.deprecation import MiddlewareMixin
from user_agents import parse

class LokiLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.loki_url = os.getenv("LOKI_URL", "https://loki.test.dev/loki/api/v1/push").rstrip('/')
        self.tags = {
            "app": os.getenv("APP_NAME", "test"),
            "environment": os.getenv("ENVIRONMENT", "test")
        }
        self.timeout = float(os.getenv("LOGGING_TIMEOUT", "5"))
        self.session = requests.Session()

    def send_to_loki(self, log_data):
        timestamp = int(time.time() * 1e9)
        payload = {"streams": [{"stream": self.tags, "values": [[str(timestamp), json.dumps(log_data)]]}]}
        try:
            response = self.session.post(
                self.loki_url,
                data=gzip.compress(json.dumps(payload).encode('utf-8')),
                headers={"Content-Type": "application/json", "Content-Encoding": "gzip"},
                timeout=self.timeout
            )
            if response.status_code != 204:
                print(f"Loki responded with status {response.status_code}: {response.text}")
        except requests.RequestException as e:
            print(f"Failed to send logs to Loki: {e}")

    def process_request(self, request):
        request.start_time = time.monotonic()
        request.client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', 'Unknown')
        request.user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

    def process_response(self, request, response):
        duration = round(time.monotonic() - getattr(request, 'start_time', time.monotonic()), 4)

        log_data = {
            "message": "API request completed" if response.status_code < 400 else "API request failed",
            "path": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration": duration,
            "client_ip": getattr(request, 'client_ip', "Unknown"),
            "os": request.user_agent.os.family or 'Unknown',
            "browser": request.user_agent.browser.family or 'Unknown',
            "device": request.user_agent.device.family or 'Unknown',
        }

        self.send_to_loki(log_data)
        return response