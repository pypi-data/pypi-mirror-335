import time
import logging
import queue
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from random import random
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from ext_llm import LlmClient
from ext_llm.llm.response import Response
from ext_llm.llm.stream import Stream
from ext_llm.scheduler_statistic import SchedulerStatistic
from ext_llm.scheduler_statistic_repository import SchedulerStatisticRepository


@dataclass(order=True)  # Make the class comparable for priority queue
class LlmRequest:
    priority: int = field(compare=True)  # First field for comparison in PriorityQueue
    id: str = field(compare=False)  # Other fields won't be used for comparison
    system_prompt: str = field(compare=False)
    prompt: str = field(compare=False)
    max_tokens: Optional[int] = field(default=None, compare=False)
    temperature: Optional[float] = field(default=None, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=5, compare=False)
    callback: Optional[Callable] = field(default=None, compare=False)


class RequestScheduler:
    def __init__(self, llm: LlmClient,
                 scheduler_statistic_repository : SchedulerStatisticRepository,
                 max_workers: int = 4,
                 max_retries: int = 5,
                 retry_delay: float = 4.0,
                 initial_rate_limit: int = 60,
                 min_rate_limit: int = 5,
                 max_rate_limit: int = 120):
        self.stop_time = None
        self.start_time = None
        self.llm = llm
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # AIMD rate limit parameters
        self.initial_rate_limit = initial_rate_limit
        self.current_rate_limit = initial_rate_limit
        self.min_rate_limit = min_rate_limit
        self.max_rate_limit = max_rate_limit
        self.additive_increase = 1  # How much to increase per success
        self.multiplicative_decrease_factor = 0.5  # Reduce by half on failure

        # Rate limit tracking
        self.success_counter = 0
        self.success_threshold = 5  # Number of consecutive successes before increasing rate
        self.rate_limit_lock = threading.RLock()  # For thread-safe rate limit adjustments

        self.request_queue = queue.PriorityQueue()
        self.futures: Dict[str, Future] = {}
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Exception] = {}

        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.rate_limiter = threading.Semaphore(self.current_rate_limit)
        self.rate_reset_timer = threading.Timer(60.0, self._reset_rate_limiter)

        self.running = False
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)

        self.scheduler_statistic_repository = scheduler_statistic_repository

    def start(self):
        """Start the scheduler."""
        self.running = True
        self.scheduler_thread.start()
        self.rate_reset_timer.start()
        self.logger.info("Request scheduler started")
        self.start_time = datetime.now()

    def stop(self):
        """Stop the scheduler and clean up resources."""
        self.running = False
        self.scheduler_thread.join(timeout=5.0)
        self.executor.shutdown(wait=False)
        self.rate_reset_timer.cancel()
        self.logger.info("Request scheduler stopped")
        self.stop_time = datetime.now()
        #compile statistics
        statistics = self._compile_statistics()
        self.scheduler_statistic_repository.save(statistics)

    def submit_request(self, system_prompt: str, prompt: str,
                       max_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       priority: int = 0,
                       callback: Optional[Callable] = None) -> str:
        """
        Submit a request to the scheduler.
        Returns a request ID that can be used to retrieve the result.
        """
        request_id = str(uuid.uuid4())
        request = LlmRequest(
            priority=priority,
            id=request_id,
            system_prompt=system_prompt,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            max_retries=self.max_retries,
            callback=callback
        )

        # Create a placeholder future to ensure the request is always tracked
        placeholder_future = Future()
        self.futures[request_id] = placeholder_future

        # Put the request in the queue
        self.request_queue.put(request)
        self.logger.debug(f"Submitted request {request_id} with priority {priority}")
        return request_id

    def get_result(self, request_id: str, timeout: Optional[float] = None) -> Response | Stream:
        """
        Get the result for a request. Blocks until the result is available.
        Raises any exception that occurred during processing.
        """
        if request_id in self.errors:
            raise self.errors[request_id]

        if request_id in self.results:
            return self.results[request_id]

        if request_id not in self.futures:
            raise KeyError(f"No request found with ID {request_id}")

        try:
            result = self.futures[request_id].result(timeout=timeout)
            return result
        except Exception as e:
            self.errors[request_id] = e
            raise

    def _scheduler_loop(self):
        """Main scheduler loop that processes requests from the queue."""
        while self.running:
            try:
                # Block for a short time, then check if we should still be running
                try:
                    request = self.request_queue.get(block=True, timeout=0.1)
                except queue.Empty:
                    continue

                # Acquire a rate limit token or requeue if not available
                if not self.rate_limiter.acquire(blocking=False):
                    self.logger.warning(f"Rate limit reached, re-queueing request {request.id}")
                    request.priority -= 1
                    self.request_queue.put(request)
                    time.sleep(1.0)
                    self.request_queue.task_done()
                    continue

                # Submit the task to the executor
                real_future: Future = self.executor.submit(
                    self._execute_request_with_retry,
                    request
                )

                # Get the placeholder future and copy the result from real_future when done
                placeholder_future = self.futures[request.id]

                def copy_result(real_f, placeholder_f=placeholder_future):
                    """Copy result or exception from real future to placeholder"""
                    try:
                        result = real_f.result()
                        placeholder_f.set_result(result)
                    except Exception as e:
                        placeholder_f.set_exception(e)

                real_future.add_done_callback(copy_result)

                # Also add the completion callback to handle storing results
                real_future.add_done_callback(
                    lambda f, req_id=request.id: self._handle_completed_request(req_id, f)
                )

                self.request_queue.task_done()

            except Exception as e:
                self.logger.exception(f"Error in scheduler loop: {e}")

    def _execute_request_with_retry(self, request: LlmRequest) -> Response | Stream:
        """Execute a request with retry logic."""
        last_exception = None

        while request.retry_count <= request.max_retries:
            try:
                self.logger.debug(f"Executing request {request.id}, attempt {request.retry_count + 1}")
                result = self.llm.generate_text(
                    request.system_prompt,
                    request.prompt,
                    request.max_tokens,
                    request.temperature
                )
                return result

            except Exception as e:
                request.retry_count += 1
                last_exception = e
                self.logger.warning(f"Request {request.id} failed (attempt {request.retry_count}): {str(e)}")
                #self._decrease_rate_limit()
                if request.retry_count <= request.max_retries:
                    # Exponential backoff
                    sleep_time = (self.retry_delay * (2 ** (request.retry_count - 1)))
                    self.logger.info(f"Retrying request {request.id} in {sleep_time} seconds...")
                    time.sleep(sleep_time)

        if last_exception:
            self.logger.error(f"Request {request.id} failed after {request.max_retries} retries")
            raise last_exception

        # This should not be reached
        raise RuntimeError("Unexpected state in retry logic")

    def _increase_rate_limit(self):
        """Increase rate limit additively"""
        with self.rate_limit_lock:
            new_limit = min(self.current_rate_limit + self.additive_increase, self.max_rate_limit)
            if new_limit > self.current_rate_limit:
                self.current_rate_limit = new_limit
                self.logger.info(f"Rate limit increased to {self.current_rate_limit}")

    def _decrease_rate_limit(self):
        """Decrease rate limit multiplicatively"""
        with self.rate_limit_lock:
            new_limit = max(int(self.current_rate_limit * self.multiplicative_decrease_factor),
                            self.min_rate_limit)
            if new_limit < self.current_rate_limit:
                self.current_rate_limit = new_limit
                self.logger.warning(f"Rate limit decreased to {self.current_rate_limit}")

    def _handle_completed_request(self, request_id: str, future: Future):
        """Handle a completed request future."""
        try:
            result = future.result()
            self.results[request_id] = result
            self.logger.debug(f"Request {request_id} completed successfully")

            # Increment success counter and potentially increase rate limit
            self.success_counter += 1
            if self.success_counter >= self.success_threshold:
                self._increase_rate_limit()
                self.success_counter = 0

            # Execute callback if provided
            if hasattr(future, '_callback') and future._callback:
                try:
                    future._callback(result)
                except Exception as e:
                    self.logger.error(f"Callback error for request {request_id}: {e}")

        except Exception as e:
            self.errors[request_id] = e
            self.logger.error(f"Request {request_id} failed: {e}")

            # Check if the error is related to rate limiting
            if self._is_rate_limit_error(e):
                self._decrease_rate_limit()
                self.success_counter = 0

    def _is_rate_limit_error(self, exception):
        """Determine if an exception is related to rate limiting"""
        # Customize this based on the API's rate limit exception patterns
        error_msg = str(exception).lower()
        return any(term in error_msg for term in
                  ['rate limit', 'too many requests', '429', 'quota exceeded',
                   'capacity', 'token limit', 'throttled'])

    def _reset_rate_limiter(self):
        """Reset the rate limiter every minute."""
        with self.rate_limit_lock:
            old_value = self.rate_limiter._value if hasattr(self.rate_limiter, '_value') else 0
            self.rate_limiter = threading.Semaphore(self.current_rate_limit)
            self.logger.debug(f"Rate limiter reset from {old_value} to {self.current_rate_limit}")

        # Schedule the next reset
        if self.running:
            self.rate_reset_timer = threading.Timer(60.0, self._reset_rate_limiter)
            self.rate_reset_timer.daemon = True
            self.rate_reset_timer.start()

    def _compile_statistics(self):
        return SchedulerStatistic(
            max_workers=self.max_workers,
            max_retries_per_request=self.max_retries,
            start_time=self.start_time,
            stop_time=self.stop_time,
            total_requests= len(self.results) + len(self.errors),
            successful_requests= len(self.results),
            failed_requests= len(self.errors),
            average_response_time= None,
            throughput= len(self.results) / (self.stop_time - self.start_time).total_seconds(),
            retries_count=None,
            average_retries_per_request=None
        )