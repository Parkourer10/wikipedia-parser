import re
import nltk
from nltk.tokenize import sent_tokenize
from typing import Optional

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
class TextProcessor:
    def __init__(self):
        self.image_keywords = {
            "thumb", "px", "file", "image", "photo", "figure", "gallery",
            "jpg", "jpeg", "png", "gif", "svg", "thumbnail", "pixels"
        }
        
        self.noise_patterns = [
            r'\d{2,4}px',           
            r'\[\[File:.*?\]\]',    
            r'\[\[Image:.*?\]\]',   
            r'\{\{.*?\}\}',         
            r'<gallery>.*?</gallery>', 
            r'width=\d+',           
            r'height=\d+',          
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.noise_patterns]

    def remove_noise(self, text: str) -> str:
        if not text:
            return ""
            
        for pattern in self.compiled_patterns:
            text = pattern.sub('', text)
        return text

    def filter_sentences(self, text: str) -> str:
        try:
            sentences = sent_tokenize(text)
            
            cleaned_sentences = []
            for sent_text in sentences:
                sent_text = sent_text.strip()
                
                if len(sent_text) < 10:
                    continue
                    
                if any(word in sent_text.lower() for word in self.image_keywords):
                    continue
                    
                if sum(c.isalpha() for c in sent_text) < len(sent_text) * 0.5:
                    continue
                    
                cleaned_sentences.append(sent_text)
            
            return " ".join(cleaned_sentences)
            
        except Exception as e:
            print(f"Warning: Sentence filtering failed: {e}")
            return text

    def process_text(self, text: str) -> Optional[str]:
        if not text:
            return None
            
        try:
            
            cleaned = self.remove_noise(text)
            filtered = self.filter_sentences(cleaned)
            filtered = re.sub(r'\s+', ' ', filtered).strip()
            
            return filtered if filtered else None
            
        except Exception as e:
            print(f"Warning: Text processing failed: {e}")
            return None 
