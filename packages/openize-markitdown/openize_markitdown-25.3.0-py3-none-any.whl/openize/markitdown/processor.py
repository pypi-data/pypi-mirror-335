import logging
from pathlib import Path
from factory import ConverterFactory
from llm_strategy import SaveLocally, InsertIntoLLM


class DocumentProcessor:
    def __init__(self, output_dir=Path("converted_md")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_document(self, file_path, insert_into_llm=False):
        file_path = Path(file_path)
        file_extension = file_path.suffix
        converter = ConverterFactory.get_converter(file_extension)

        if not converter:
            logging.warning(f"No converter available for {file_extension}")
            return

        md_file = converter.convert_to_md(file_path, self.output_dir)
        if md_file:
            strategy = InsertIntoLLM() if insert_into_llm else SaveLocally()
            strategy.process(md_file)

