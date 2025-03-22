from queue import Queue
from threading import Thread
from typing import Union

from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

from vajra.datatypes import TokenizerOutput
from vajra.utils.threading_utils import exit_on_error


class TokenizerWorker:
    def __init__(
        self,
        input_queue: Queue,
        output_queue: Queue,
        tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
    ):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.tokenizer = tokenizer

    def start(self):
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    @exit_on_error
    def run(self):
        while True:
            tokenizer_input = self.input_queue.get()
            self.output_queue.put(
                TokenizerOutput(
                    tokenizer_input.seq_id,
                    tokenizer_input.arrival_time,
                    tokenizer_input.prompt,
                    self.tokenizer.encode(tokenizer_input.prompt),
                    tokenizer_input.sampling_params,
                )
            )
