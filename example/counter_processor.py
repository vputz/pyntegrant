from collections import Counter

from interfaces import Processor


class CounterProcessor(Processor):
    def process_input(self, s: str) -> dict:
        c = Counter(s)
        total_chars = len(s)
        distinct_chars = len(c)

        return dict(
            total_chars=total_chars, distinct_chars=distinct_chars, character_count=c
        )
