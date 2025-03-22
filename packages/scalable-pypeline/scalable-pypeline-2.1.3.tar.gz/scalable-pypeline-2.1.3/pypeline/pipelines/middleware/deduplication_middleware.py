import dramatiq
import signal
from dramatiq.middleware import Middleware
from pypeline.barrier import LockingParallelBarrier
from pypeline.constants import DEFAULT_TASK_TTL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeduplicationMiddleware(Middleware):
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.active_locks = {}

    def before_process_message(self, broker, message):
        task_id = message.message_id
        task_key = f"dramatiq:task_counter:{task_id}"
        lock_key = f"dramatiq:lock:{task_id}"
        try:
            # Try to acquire a lock for the task
            locking_parallel_barrier = LockingParallelBarrier(
                self.redis_url,
                task_key=task_key,
                lock_key=lock_key,
            )
            if (
                locking_parallel_barrier.get_task_count() > 0
                or not locking_parallel_barrier.acquire_lock(timeout=DEFAULT_TASK_TTL)
            ):
                logger.info(f"Found duplicate task {task_id}.  Skipping...")
                raise dramatiq.middleware.SkipMessage(
                    f"Task {task_id} is already being processed."
                )

            locking_parallel_barrier.set_task_count(1)
            # Store the lock reference in the message and track it globally
            message.options["dedupe_task_key"] = task_key
            message.options["dedupe_lock_key"] = lock_key
            self.active_locks[lock_key] = locking_parallel_barrier
        except dramatiq.middleware.SkipMessage:
            raise dramatiq.middleware.SkipMessage(
                f"Task {task_id} is already being processed."
            )
        except Exception as e:
            logger.exception(e)
            raise e

    def after_process_message(self, broker, message, *, result=None, exception=None):
        """Releases lock for the message that just finished."""
        dedupe_task_key = message.options.get("dedupe_task_key", None)
        dedupe_lock_key = message.options.get("dedupe_lock_key", None)
        if not dedupe_lock_key or not dedupe_task_key:
            logger.warning(
                "unexpected in after_process_message: dedupe task or lock key not in message"
            )
            return
        if dedupe_lock_key in self.active_locks:
            try:
                lock = self.active_locks[dedupe_lock_key]
                lock.decrement_task_count()
                lock.release_lock()
                del self.active_locks[dedupe_lock_key]
            except Exception as e:
                logger.info(
                    f"Exception while trying to release lock {dedupe_lock_key}: {e}"
                )
                raise e
        else:
            lock = LockingParallelBarrier(
                self.redis_url,
                task_key=dedupe_task_key,
                lock_key=dedupe_lock_key,
            )
            lock.decrement_task_count()
            lock.release_lock()

    def before_worker_shutdown(self, *args):
        self.release_all_locks()

    def before_worker_thread_shutdown(self, *args):
        self.release_all_locks()

    def release_all_locks(self, *args):
        """Release all locks when the worker shuts down."""
        for lock_key, lock in self.active_locks.items():
            try:
                lock.decrement_task_count()
                lock.release_lock()
            except Exception as e:
                logger.info(f"Exception while trying to release lock {lock_key}: {e}")
                raise e
        self.active_locks.clear()
