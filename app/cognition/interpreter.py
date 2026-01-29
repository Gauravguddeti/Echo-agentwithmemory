from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.dependencies import get_llm

class NormalizedText(BaseModel):
    clean_text: str = Field(description="Normalized text with slang removed, drive letters fixed (D -> D:\\), and fillers removed.")
    confidence: float = Field(description="Confidence from 0.0 to 1.0")

class Interpreter:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=NormalizedText)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Text Normalizer.
Target: Normalize user input for an OS Agent.
Rules:
1. Remove slang ("brev", "pls", "ya") and fillers.
2. Preserve meaning strictly.
3. Normalize drive letters: "D folder" -> "D:\\folder". "C drive" -> "C:\\".
4. Do NOT change filenames or content intended for writing.
5. If text is already clean, return it as is.
6. Return JSON matching the schema.
"""),
            ("human", "{text}\n\n{format_instructions}")
        ])

    async def normalize(self, text: str) -> NormalizedText:
        chain = self.prompt | self.llm | self.parser
        try:
            return await chain.ainvoke({
                "text": text,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            # Fallback for simple errors
            print(f"[Interpreter] Error: {e}. Returning raw text.")
            return NormalizedText(clean_text=text, confidence=0.5)

interpreter = Interpreter()
