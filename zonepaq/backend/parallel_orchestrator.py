import itertools
import logging as log
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from backend.logger import log


class ThreadExecutor:
    def __init__(self, max_workers=None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers or os.cpu_count())
        self.lock = Lock()

    def run(self, func, *args, **kwargs):
        return self.executor.submit(func, *args, **kwargs)

    def shutdown(self):
        self.executor.shutdown(wait=True)


class TaskRetryManager:
    def __init__(self, executor: ThreadExecutor):
        self.executor = executor
        self.lock = Lock()

    def execute_tasks_with_retries(
        self, files, func, batch_size=10, timeout=13, max_retries=2
    ):
        results_ok = {}
        results_ko = {}
        futures = {}
        retry_count = {}

        try:
            for batch in itertools.zip_longest(*[iter(files)] * batch_size):
                batch = list(filter(None, batch))
                if not batch:
                    break

                with self.lock:
                    futures.update(
                        {self.executor.run(func, file): file for file in batch}
                    )

                for future in as_completed(futures):
                    file = None
                    with self.lock:
                        file = futures.pop(future, None)

                    if not file:
                        continue
                    try:
                        success, result = future.result(timeout=timeout)
                        with self.lock:
                            if success:
                                results_ok[file] = result
                            else:
                                results_ko[file] = result
                    except TimeoutError:
                        with self.lock:
                            retry_count[file] = retry_count.get(file, 0) + 1

                        if retry_count[file] <= max_retries:
                            log.warning(
                                f"Retrying {file} (attempt {retry_count[file]})"
                            )
                            with self.lock:
                                futures[self.executor.run(func, file)] = file
                        else:
                            log.error(f"Timeout after retries for {file}")
                            with self.lock:
                                results_ko[file] = "Timeout"
                    except Exception as e:
                        log.error(f"Error processing {file}: {e}")
                        with self.lock:
                            results_ko[file] = str(e)
        finally:
            with self.lock:
                for future in futures:
                    if not future.done():
                        future.cancel()
            self.executor.shutdown()

        return results_ok, results_ko


class ThreadManager:
    @staticmethod
    def run_in_thread_with_result(target_func, timeout=3, *args, **kwargs):
        result_container = {}

        def wrapper():
            try:
                target_func(result_container, *args, **kwargs)
            except Exception as e:
                result_container["exception"] = e

        thread = threading.Thread(target=wrapper)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            log.error("Timeout expired for thread execution.")
            result_container["timeout"] = True

        return result_container

    @staticmethod
    def run_in_background(target_func, daemon=True, *args, **kwargs):
        thread = threading.Thread(
            target=target_func, args=args, kwargs=kwargs, daemon=daemon
        )
        thread.start()
        return thread


class SubprocessManager:
    @staticmethod
    def handle_errors(result_container, context):
        if result_container.get("timeout"):
            log.error(f"Timeout expired for {context}.")
            return False, "Timeout expired"

        if "exception" in result_container:
            log.exception(f"An error occurred during {context}.")
            return False, str(result_container["exception"])

        if result_container.get("returncode") != 0:
            stderr = result_container.get("stderr", "").strip()
            log.error(f"Command failed during {context}: {stderr}")
            return False, f"Command failed with error:\n{stderr}"

        return True, result_container.get("stdout", "").strip()

    @staticmethod
    def execute_subprocess(result_container, command):
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()
            result_container["stdout"] = stdout
            result_container["stderr"] = stderr
            result_container["returncode"] = process.returncode
        except Exception as e:
            result_container["exception"] = e
