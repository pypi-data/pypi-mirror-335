from processor import DocumentProcessor


class MarkItDown:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def convert_document(self, input_file, insert_into_llm=False):
        """Run the document conversion process."""
        processor = DocumentProcessor(self.output_dir)
        processor.process_document(input_file, insert_into_llm)
