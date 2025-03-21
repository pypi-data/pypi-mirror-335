class SchedulerStatistic:
    def __init__(self, max_workers,
                 max_retries_per_request,
                 start_time,
                 stop_time,
                 total_requests,
                 successful_requests,
                 failed_requests,
                 average_response_time,
                 throughput,
                 retries_count,
                 average_retries_per_request,
                 ):
        self.max_workers = max_workers
        self.max_retries_per_request = max_retries_per_request
        self.start_time = start_time
        self.stop_time = stop_time
        self.total_requests = total_requests
        self.successful_requests = successful_requests
        self.failed_requests = failed_requests
        self.average_response_time = average_response_time
        self.throughput = throughput
        self.retries_count = retries_count
        self.average_retries_per_request = average_retries_per_request
