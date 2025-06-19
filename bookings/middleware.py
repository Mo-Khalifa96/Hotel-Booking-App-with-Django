from bookings.startup import run_startup_tasks

class StartupSchedulerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.has_run = False

    def __call__(self, request):
        if not self.has_run:
            run_startup_tasks()
            self.has_run = True

        response = self.get_response(request)
        return response
