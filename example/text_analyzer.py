from interfaces import Input, Output, Processor


class TextAnalyzer:
    def __init__(self, input: Input, processor: Processor, output: Output):
        self.input = input
        self.processor = processor
        self.output = output

    def process(self):
        return self.output.format_output(
            self.processor.process_input(self.input.get_input())
        )
