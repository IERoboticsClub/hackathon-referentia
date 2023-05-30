import os
from io import StringIO
from sentence_transformers import SentenceTransformer
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import torch
from utils.common import LOG


def ocr_files(tempDir: str) -> dict:
    """This function reads the pdfs and returns a dictionary of sentences"""
    sentences = {}
    books = os.listdir(tempDir)
    
    for book in books:
        with open(f'{tempDir}/{book}', 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            sentences[book] = {}
            for i, page in enumerate(PDFPage.create_pages(doc)):
                output_string = StringIO()
                device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)
                text = output_string.getvalue()
                sentences[book][i] = text.replace(".  \n", ".\n").split(".\n")
                for sentence in sentences[book][i]:
                    sentence_processed = sentence.replace("\n", "").replace("  ", " ").replace("-", "")
                    sentences[book][i][sentences[book][i].index(sentence)] = sentence_processed
            output_string.truncate(0)
            output_string.seek(0)
    return sentences


def load_tokenizer_database() -> SentenceTransformer:
    """This function loads the tokenizer
    Uses a BERT based sentence transformer 
    """
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')
    return model


# def load_tokenizer_inference(model: str): 
#     """This function loads the tokenizer for inference"""
#     print(f"Loading tokenizer {model}")
#     #return RobertaTokenizer.from_pretrained(f"{model}")
#     return RobertaTokenizer.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")


def get_embedding(sentence: str, tokenizer: SentenceTransformer) -> torch.Tensor:
    """This function returns the embedding of a sentence"""
    embedding = tokenizer.encode(sentence)
    return embedding


def get_db_schema(sentences: dict) -> dict:
    """This function returns a dictionary with all db schema values (including embeddings) for each sentence"""
    aux_dict = dict()
    tokenizer = load_tokenizer_database()
    for doc in sentences.keys():
        for page in sentences[doc].keys():
            for sentence in sentences[doc][page]:
                embedded_text = get_embedding(sentence, tokenizer)
                LOG.info(f"Embedding the text:", len(embedded_text))
                aux_dict[str(doc + str(page) + sentence)] = [str(doc + str(page) + sentence), str(page), doc, sentence, embedded_text]
    return aux_dict