import pytest
from pathlib import Path
from ..src.openize.markitdown.converters import WordConverter, PDFConverter, ExcelConverter, PowerPointConverter
from ..src.openize.markitdown.factory import ConverterFactory
from ..src.openize.markitdown.llm_strategy import SaveLocally, InsertIntoLLM
from ..src.openize.markitdown.processor import DocumentProcessor
import os

@pytest.fixture
def sample_output_dir():
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    return output_dir

@pytest.fixture
def sample_md_file(sample_output_dir):
    md_file = sample_output_dir / "sample.md"
    md_file.write_text("# Sample Markdown File\n\nThis is a test.")
    return md_file

# Test Converters
def test_word_converter(sample_output_dir):
    converter = WordConverter()
    assert converter is not None

def test_pdf_converter(sample_output_dir):
    converter = PDFConverter()
    assert converter is not None

def test_excel_converter(sample_output_dir):
    converter = ExcelConverter()
    assert converter is not None

def test_ppt_converter(sample_output_dir):
    converter = PowerPointConverter()
    assert converter is not None

# Test ConverterFactory
def test_converter_factory():
    assert isinstance(ConverterFactory.get_converter(".docx"), WordConverter)
    assert isinstance(ConverterFactory.get_converter(".pdf"), PDFConverter)
    assert isinstance(ConverterFactory.get_converter(".xlsx"), ExcelConverter)
    assert isinstance(ConverterFactory.get_converter(".pptx"), PowerPointConverter)


# Test LLM Strategy
def test_save_locally(sample_md_file):
    strategy = SaveLocally()
    strategy.process(sample_md_file)
    assert sample_md_file.exists()

def test_insert_into_llm(mocker, sample_md_file):
    mocker.patch("openai.ChatCompletion.create", return_value={"choices": [{"message": {"content": "LLM Response"}}]})
    strategy = InsertIntoLLM()
    strategy.process(sample_md_file)

# Test DocumentProcessor
def test_document_processor(mocker, sample_output_dir):
    mocker.patch("packages.src.openize.markitdown.factory.ConverterFactory.get_converter", return_value=WordConverter())
    processor = DocumentProcessor(output_dir=sample_output_dir)
    processor.process_document("sample.docx", insert_into_llm=False)
    output_file = sample_output_dir / "sample.md"
    assert output_file.exists()

if __name__ == "__main__":
    pytest.main()
