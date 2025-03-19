from abc import abstractmethod
from collections import defaultdict
from queue import PriorityQueue
from typing import Any, Dict, List, Optional

from vajra._native.scheduler import BatchFormationTracker as NativeBatchFormationTracker
from vajra._native.scheduler import KvpStateTracker as KvpStateTracker
from vajra.config import (
    BaseReplicaSchedulerConfig,
    CacheConfig,
    ModelConfig,
    ParallelConfig,
)
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import SequenceStatus  # type: ignore
from vajra.datatypes import SequenceWithPriority  # type: ignore
from vajra.logger import init_logger
from vajra.metrics_store import MetricsStore  # type: ignore
from vajra.utils.threading_utils import synchronized

logger = init_logger(__name__)

MAX_NUM_SKIPPED_SEQS = 10


class BaseReplicaScheduler:
    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: BaseReplicaSchedulerConfig,
        cache_config: CacheConfig,
        parallel_config: ParallelConfig,
        waiting_queue: PriorityQueue,
    ) -> None:
        self.metrics_store = MetricsStore.get_instance()
        self.model_config = model_config
        self.scheduler_config = scheduler_config
        self.cache_config = cache_config
        self.parallel_config = parallel_config

        # Initialize the KVP manager
        self.kvp_state_tracker = KvpStateTracker(
            model_config=model_config.native_handle,
            cache_config=cache_config.native_handle,
            parallel_config=parallel_config.native_handle,
        )

        # we maintain this just for logging purposes
        self._iteration_id = 0

        self.prompt_limit = model_config.max_model_len

        # number of running batches should be less than or equal to the number of pipeline stages
        self.num_running_batches = 0
        self.num_running_stages = 0

        self.seq_block_counter: Dict[str, int] = defaultdict(int)

        # Sequence groups in the WAITING state.
        self.waiting: PriorityQueue = waiting_queue
        # Sequence groups in the RUNNING state.
        self.running: List[Sequence] = []
        # Sequences that are in the middle of prefilling.
        self.partial_prefill_seqs: PriorityQueue = PriorityQueue()

        self.last_batch_execution_time: Optional[float] = None

    def reset_state(self) -> None:
        self._iteration_id = 0
        self.last_batch_execution_time = None

    def _get_batch_formation_tracker(self) -> NativeBatchFormationTracker:
        return NativeBatchFormationTracker(
            schedule_id=self._iteration_id,
            max_micro_batch_size=self.scheduler_config.max_batch_size,
            kvp_state_tracker=self.kvp_state_tracker,
        )

    @synchronized
    def add_seq(self, seq: Sequence) -> None:
        # Add sequence groups to the waiting queue.
        wrapped_seq = SequenceWithPriority(
            priority=self._get_seq_priority(seq), seq=seq
        )
        self.waiting.put(wrapped_seq)

    @synchronized
    def add_partial_prefill_seq(self, seq: Sequence) -> None:
        # Add sequence to the partial prefill queue
        wrapped_seq = SequenceWithPriority(
            priority=self._get_seq_priority(seq), seq=seq
        )
        self.partial_prefill_seqs.put(wrapped_seq)

    def has_unfinished_seqs(self) -> bool:
        return (
            (not self.waiting.empty())
            or (not self.partial_prefill_seqs.empty())
            or self.running
        )

    def get_num_unfinished_seqs(self) -> int:
        return (
            self.waiting.qsize() + self.partial_prefill_seqs.qsize() + len(self.running)
            > 0
        )

    @abstractmethod
    def _get_seq_priority(self, seq: Sequence) -> Any:
        pass

    def _sort_waiting_queue(self) -> None:
        self.waiting.sort(key=lambda x: x[0])

    def _preempt(
        self,
        seq: Sequence,
    ) -> None:
        assert seq.is_executing()
        self._free_seq(seq)
        self.add_seq(seq)

    def _allocate(self, seq: Sequence) -> bool:
        """
        We use a naive approach to allocate memory where we allocate all the memory
        required by the seq in one go. This is because we expect the compute requirement
        to far exceed the memory requirement. In KVP, incremental memory allocation can
        lead to deadlocks -- where multiple long seqs are waiting for memory to be available
        on a new kvp group, but none of them can proceed because the memory is not available.
        TODO(amey): This is a naive approach and can be improved in the future. Especially, offloading
        memory allocation to CPU can be a good solution, especially for longer seqs.
        While allocating memory, we must choose the kvp groups such that we have minimal
        compute contention. While also ensuring that we don't create memory hotspots.
        The allocate method offloads this responsibility to _get_allocation_order method.
        Args:
            seq: The sequence to allocate memory for

        Returns:
            bool: True if allocation was successful, False otherwise
        """
        # if seq is already allocated, return
        if seq.seq_id in self.seq_block_counter:
            return True

        # Delegate allocation to the KVP manager
        status, num_blocks = self.kvp_state_tracker.allocate(seq)
        if status:
            self.seq_block_counter[seq.seq_id] = num_blocks
        return status

    def _free_seq(self, seq: Sequence) -> None:
        """Free memory allocated for a sequence"""
        self.kvp_state_tracker.free_seq(seq)
        del self.seq_block_counter[seq.seq_id]

    def _append_slot(self, seq: Sequence) -> bool:
        """Increment the block counter if a new block has been allocated"""
        num_total_blocks = self.seq_block_counter[seq.seq_id]
        has_appended = self.kvp_state_tracker.append_slot(seq, num_total_blocks)
        if has_appended:
            self.seq_block_counter[seq.seq_id] += 1
        return has_appended

    def _ensure_can_append_slot(
        self, seq: Sequence, batch_formation_tracker: NativeBatchFormationTracker
    ) -> bool:
        """Ensure that a slot can be appended to the sequence, potentially by preempting other sequences"""
        if self.kvp_state_tracker.can_append_slot(seq):
            return True

        could_ensure_memory = False

        # Find the last seq that contains allocation on the last kv group
        # Check partial prefill list first (in reverse) assuming fcfs
        max_seq = None
        max_idx = -1

        for idx, seq in enumerate(self.partial_prefill_seqs.queue):
            if max_seq is None or seq.priority > max_seq.priority:
                max_seq = seq
                max_idx = idx

        priority_seq = self.partial_prefill_seqs.queue.pop(max_idx)
        batch_formation_tracker.add_preempted_sequence(priority_seq.seq)
        could_ensure_memory = True

        # If we haven't found space yet, check running list in reverse, assuming fcfs
        if not could_ensure_memory:
            for idx, priority_seq in enumerate(reversed(self.running)):
                assert self.kvp_state_tracker.get_last_kv_group_id(
                    priority_seq
                ) in self.kvp_state_tracker.get_kvp_group_block_counter(
                    priority_seq.seq_id
                ), "Running seq is not allocated on the last kv group"
                self.running.pop(len(self.running) - 1 - idx)
                self._preempt(priority_seq)
                batch_formation_tracker.add_preempted_sequence(priority_seq)
                could_ensure_memory = True
                break

        # If still no space, preempt the input sequence
        if not could_ensure_memory:
            self._preempt(seq)
            batch_formation_tracker.add_preempted_sequence(seq)

        return could_ensure_memory

    def on_stage_completed(self, seqs: List[Sequence]) -> None:
        self.num_running_stages -= 1

        for seq in seqs:
            assert not seq.is_finished()

            if not seq.is_paused():
                continue

            assert not seq.prompt_stage_processing_finished, "Unreachable state."
            self.add_partial_prefill_seq(seq)

    def on_step_completed(self, seqs: List[Sequence], execution_time: float) -> None:
        self.num_running_batches -= 1
        if not self.parallel_config.pipeline_parallel_size > 1:
            self.num_running_stages -= 1

        self.last_batch_execution_time = execution_time

        for seq in seqs:
            if seq.is_finished():
                self._free_seq(seq)
                continue

            if not seq.is_paused():
                continue

            if seq.prompt_processing_finished:
                self.running.append(seq)
            elif not self.parallel_config.enable_sequence_pipeline_parallel:
                # TODO(Amey): Rethink the running/paused transitions split between seq manager & scheduler
                self.add_partial_prefill_seq(seq)

    def _check_seq_prompt_length(self, seq: Sequence) -> bool:
        return seq.prompt_len <= self.kvp_state_tracker.get_max_seq_len()

    def is_seq_allocated(self, seq_id: str) -> bool:
        return seq_id in self.seq_block_counter

    @abstractmethod
    def _get_seq_next_num_q_tokens(
        self, seq: Sequence, batch_formation_tracker: NativeBatchFormationTracker
    ) -> int:
        pass

    @synchronized
    def _schedule(self) -> SchedulerOutput:
        batch_formation_tracker = self._get_batch_formation_tracker()
        num_skipped_seqs = 0

        # First we handle the running sequences
        while self.running:
            seq = self.running[0]

            assert not seq.is_finished()
            assert seq.prompt_stage_processing_finished
            assert seq.is_paused()

            if not batch_formation_tracker.can_add_sequences():
                break

            if not self._ensure_can_append_slot(seq, batch_formation_tracker):
                continue

            self._append_slot(seq)
            if not batch_formation_tracker.can_add_sequences():
                num_skipped_seqs += 1
                continue

            self.running.pop(num_skipped_seqs)

            batch_formation_tracker.add_sequence(
                seq,
                1,
            )

        # Then handle waiting and partial prefill queues
        while num_skipped_seqs < MAX_NUM_SKIPPED_SEQS:
            # Try to peek at both queues
            waiting_seq = None
            partial_seq = None

            waiting_seq = self.waiting.queue[0] if not self.waiting.empty() else None

            partial_seq = (
                self.partial_prefill_seqs.queue[0]
                if not self.partial_prefill_seqs.empty()
                else None
            )

            # If both queues are empty, break
            if waiting_seq is None and partial_seq is None:
                break

            # Choose the sequence with higher priority (lower value)
            seq_with_priority = None
            from_waiting_queue = False  # Track which queue we got it from
            if waiting_seq is not None and partial_seq is not None:
                # comparing priorities
                if waiting_seq < partial_seq:
                    seq_with_priority = self.waiting.get()
                    from_waiting_queue = True
                else:
                    seq_with_priority = self.partial_prefill_seqs.get()
            elif waiting_seq is not None:
                seq_with_priority = self.waiting.get()
                from_waiting_queue = True
            else:
                seq_with_priority = self.partial_prefill_seqs.get()

            seq = seq_with_priority.seq

            if not self._check_seq_prompt_length(seq):
                batch_formation_tracker.add_ignored_sequence(seq)
                seq.status = SequenceStatus.FINISHED_IGNORED
                logger.warning(
                    f"Ignoring seq_id: {seq.seq_id} due to max seq length limit."
                )
                # confirm dont need to add back
                continue

            if not batch_formation_tracker.can_add_sequences():
                # Put the sequence back in its original queue
                if from_waiting_queue:
                    self.waiting.put(seq_with_priority)
                else:
                    self.partial_prefill_seqs.put(seq_with_priority)
                break

            assert not seq.prompt_stage_processing_finished
            assert not seq.is_finished()

            assert (
                seq.is_paused() or seq.is_waiting_preempted() or seq.is_waiting()
            ), f"seq_id: {seq.seq_id}, status: {seq.status}"

            if not self._allocate(seq):
                num_skipped_seqs += 1
                # Put back in original queue
                if from_waiting_queue:
                    self.waiting.put(seq_with_priority)
                else:
                    self.partial_prefill_seqs.put(seq_with_priority)
                continue

            num_q_tokens = self._get_seq_next_num_q_tokens(seq, batch_formation_tracker)

            if num_q_tokens == 0:
                num_skipped_seqs += 1
                # Put back in original queue
                if from_waiting_queue:
                    self.waiting.put(seq_with_priority)
                else:
                    self.partial_prefill_seqs.put(seq_with_priority)
                continue

            batch_formation_tracker.add_sequence(
                seq,
                num_q_tokens,
            )

        batch = batch_formation_tracker.get_batch()

        return batch

    def schedule(self) -> SchedulerOutput:
        # Schedule sequence groups.
        # This function call changes the internal states of the scheduler
        # such as self.running and self.waiting.
        self._iteration_id += 1

        if (
            self.num_running_batches >= self.parallel_config.pipeline_parallel_size
            or self.num_running_stages != 0
        ):
            return SchedulerOutput(
                self._iteration_id,
                ignored_seq_ids=[],
                preempted_seq_ids=[],
                seq_schedule_metadata_list=[],
            )

        scheduler_output = self._schedule()

        if not scheduler_output.is_empty:
            self.num_running_batches += 1
            self.num_running_stages += 1

        return scheduler_output

    def free_finished_seqs(self) -> None:
        for seq in self.running:
            if seq.is_finished():
                self._free_seq(seq)
        self.running = [seq for seq in self.running if not seq.is_finished()]
