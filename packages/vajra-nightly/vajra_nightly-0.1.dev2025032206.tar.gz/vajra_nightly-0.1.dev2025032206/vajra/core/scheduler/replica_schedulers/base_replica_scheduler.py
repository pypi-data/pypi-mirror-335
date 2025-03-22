from abc import abstractmethod
from collections import defaultdict
from queue import Empty, PriorityQueue
from typing import Dict, List, Optional, Tuple

from vajra._native.core.scheduler.replica_schedulers.trackers import (
    BatchFormationTracker,
    KvpStateTracker,
)
from vajra.config import (
    BaseReplicaSchedulerConfig,
    CacheConfig,
    ModelConfig,
    ParallelConfig,
)
from vajra.core.scheduler.request_prioritizers import BaseRequestPrioritizer
from vajra.core.scheduler.request_prioritizers.base_request_prioritizer import (
    BaseSequenceWithPriority,
)
from vajra.datatypes import SchedulerOutput, Sequence, SequenceStatus
from vajra.logger import init_logger
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
        num_gpu_blocks: int,
        waiting_queue: PriorityQueue,
        request_prioritizer: BaseRequestPrioritizer,
    ) -> None:
        self.model_config: ModelConfig = model_config
        self.scheduler_config: BaseReplicaSchedulerConfig = scheduler_config
        self.cache_config: CacheConfig = cache_config
        self.parallel_config: ParallelConfig = parallel_config
        self.request_prioritizer: BaseRequestPrioritizer = request_prioritizer

        # Initialize the KVP manager
        self.kvp_state_tracker: KvpStateTracker = KvpStateTracker(
            model_config=model_config.native_handle,
            cache_config=cache_config.native_handle,
            parallel_config=parallel_config.native_handle,
            num_gpu_blocks=num_gpu_blocks,
        )

        # we maintain this just for logging purposes
        self.iteration_id: int = 0

        self.prompt_limit: int = model_config.max_model_len

        # number of running batches should be less than or equal to the number of pipeline stages
        self.num_running_batches: int = 0
        self.num_running_stages: int = 0

        self.seq_block_counter: Dict[str, int] = defaultdict(int)

        # Sequence groups in the WAITING state.
        self.waiting: PriorityQueue = waiting_queue
        # Sequence groups in the RUNNING state.
        self.running: List[Sequence] = []
        # Sequences that are in the middle of prefilling.
        self.partial_prefills: PriorityQueue = PriorityQueue()

        self.last_batch_execution_time: Optional[float] = None

    def reset_state(self) -> None:
        self.iteration_id = 0
        self.last_batch_execution_time = None

    def _get_batch_formation_tracker(self) -> BatchFormationTracker:
        return BatchFormationTracker(
            schedule_id=self.iteration_id,
            max_micro_batch_size=self.scheduler_config.max_batch_size,
            kvp_state_tracker=self.kvp_state_tracker,
        )

    def add_partial_prefill(self, seq: Sequence) -> None:
        # Add sequence to the partial prefill queue
        self.partial_prefills.put(self.request_prioritizer.get_seq_with_priority(seq))

    def _preempt(
        self,
        seq: Sequence,
    ) -> None:
        assert seq.is_executing()
        self._free_seq(seq)
        self.waiting.put(self.request_prioritizer.get_seq_with_priority(seq))

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
        self, input_seq: Sequence, batch_formation_tracker: BatchFormationTracker
    ) -> bool:
        """Ensure that a slot can be appended to the sequence, potentially by preempting other sequences"""
        if self.kvp_state_tracker.can_append_slot(input_seq):
            return True

        # Find the last seq that contains allocation on the last kv group
        # Check partial prefill list first (in reverse) assuming fcfs
        least_priority_seq: Optional[BaseSequenceWithPriority] = None
        least_priority_seq_idx: int = -1

        # Find the least priority seq in the partial prefill queue
        # Note that we can easily find the highest priority seq in a priority queue
        # but finding the least priority seq requires a linear scan
        for idx, seq_with_priority in enumerate(self.partial_prefills.queue):
            if (
                least_priority_seq is None
                or seq_with_priority.get_priority() > least_priority_seq.get_priority()
            ):
                least_priority_seq = seq_with_priority
                least_priority_seq_idx = idx

        # If we find a seq that can be preempted, preempt it
        if least_priority_seq is not None:
            seq_with_priority = self.partial_prefills.queue.pop(least_priority_seq_idx)
            assert least_priority_seq.seq.seq_id == seq_with_priority.seq.seq_id
            # _ensure_can_append_slot should only be called with running seqs
            assert input_seq.seq_id != seq_with_priority.seq.seq_id
            self._preempt(seq_with_priority.seq)
            batch_formation_tracker.add_preempted_sequence(seq_with_priority.seq)
            return True

        # If we haven't found space yet, check running list in reverse
        # NOTE: This is a naive approach that assumes fcfs behavior
        for idx, seq in enumerate(reversed(self.running)):
            last_kv_group_id = self.kvp_state_tracker.get_last_kv_group_id(seq)
            assert (
                last_kv_group_id
                in self.kvp_state_tracker.get_kvp_group_block_counter(input_seq.seq_id)
            ), ("Running seq is not allocated on the last kv group")
            self.running.pop(len(self.running) - 1 - idx)
            self._preempt(seq)
            batch_formation_tracker.add_preempted_sequence(seq)

            # If the preempted sequence is not the input sequence, return True
            return seq.seq_id != input_seq.seq_id

        raise RuntimeError("Unreachable condition reached")

    def on_stage_completed(self, seqs: List[Sequence]) -> None:
        self.num_running_stages -= 1

        for seq in seqs:
            assert not seq.is_finished()

            if not seq.is_paused():
                continue

            assert not seq.prompt_stage_processing_finished, "Unreachable state."
            self.add_partial_prefill(seq)

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
                self.add_partial_prefill(seq)

    def _check_seq_prompt_length(self, seq: Sequence) -> bool:
        return seq.prompt_len <= self.kvp_state_tracker.get_max_seq_len()

    def is_seq_allocated(self, seq_id: str) -> bool:
        return seq_id in self.seq_block_counter

    @abstractmethod
    def _get_seq_next_num_q_tokens(
        self, seq: Sequence, batch_formation_tracker: BatchFormationTracker
    ) -> int:
        pass

    @synchronized
    def _schedule(self) -> Tuple[SchedulerOutput, List[Sequence]]:
        batch_formation_tracker = self._get_batch_formation_tracker()
        num_skipped_seqs = 0
        new_seqs: List[Sequence] = []

        # First we handle the running sequences
        while self.running:
            seq = self.running[num_skipped_seqs]

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
            partial_prefill_seq = None

            if not self.waiting.empty():
                # there are other schedulable entities
                # so get the next seq from the waiting queue without blocking
                try:
                    waiting_seq = self.waiting.get(block=False)
                except Empty:
                    pass

            if not self.partial_prefills.empty():
                # If the partial prefill queue is not empty, get the next seq
                partial_prefill_seq = self.partial_prefills.get()

            # If both queues are empty, break
            if not waiting_seq and not partial_prefill_seq:
                break

            waiting_seq_priority = (
                waiting_seq.get_priority() if waiting_seq else float("inf")
            )
            partial_prefill_seq_priority = (
                partial_prefill_seq.get_priority()
                if partial_prefill_seq
                else float("inf")
            )

            seq_with_priority: Optional[BaseSequenceWithPriority] = None
            seq_source: Optional[PriorityQueue] = None

            if waiting_seq_priority < partial_prefill_seq_priority:
                assert waiting_seq
                seq_with_priority = waiting_seq
                seq_source = self.waiting
                if partial_prefill_seq:
                    self.partial_prefills.put(partial_prefill_seq)
            else:
                assert partial_prefill_seq
                seq_with_priority = partial_prefill_seq
                seq_source = self.partial_prefills
                if waiting_seq:
                    self.waiting.put(waiting_seq)

            assert seq_with_priority
            assert seq_source

            seq: Sequence = seq_with_priority.seq

            if not self._check_seq_prompt_length(seq):
                batch_formation_tracker.add_ignored_sequence(seq)
                seq.status = SequenceStatus.FINISHED_IGNORED
                logger.warning(
                    f"Ignoring seq_id: {seq.seq_id} due to max seq length limit."
                )
                continue

            if not batch_formation_tracker.can_add_sequences():
                # Put the sequence back in its original queue
                seq_source.put(seq_with_priority)
                break

            assert not seq.prompt_stage_processing_finished
            assert not seq.is_finished()

            assert (
                seq.is_paused() or seq.is_waiting_preempted() or seq.is_waiting()
            ), f"seq_id: {seq.seq_id}, status: {seq.status}"

            if not self._allocate(seq):
                num_skipped_seqs += 1
                # Put back in original queue
                seq_source.put(seq_with_priority)
                continue

            num_q_tokens = self._get_seq_next_num_q_tokens(seq, batch_formation_tracker)

            if num_q_tokens == 0:
                num_skipped_seqs += 1
                # Put back in original queue
                seq_source.put(seq_with_priority)
                continue

            if seq.is_waiting():
                new_seqs.append(seq)

            batch_formation_tracker.add_sequence(
                seq,
                num_q_tokens,
            )

        batch = batch_formation_tracker.get_batch()

        return batch, new_seqs

    def schedule(self) -> Tuple[SchedulerOutput, List[Sequence]]:
        # Schedule sequence groups.
        # This function call changes the internal states of the scheduler
        # such as self.running and self.waiting.
        self.iteration_id += 1

        if (
            self.num_running_batches >= self.parallel_config.pipeline_parallel_size
            or self.num_running_stages != 0
        ):
            return (
                SchedulerOutput(
                    self.iteration_id,
                    ignored_seq_ids=[],
                    preempted_seq_ids=[],
                    seq_schedule_metadata_list=[],
                ),
                [],
            )

        scheduler_output, new_seqs = self._schedule()

        if not scheduler_output.is_empty:
            self.num_running_batches += 1
            self.num_running_stages += 1

        return scheduler_output, new_seqs

    def free_finished_seqs(self) -> None:
        for seq in self.running:
            if seq.is_finished():
                self._free_seq(seq)
        self.running = [seq for seq in self.running if not seq.is_finished()]
