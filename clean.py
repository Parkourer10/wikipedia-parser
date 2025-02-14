import re
from typing import Optional

class WikipediaTextCleaner:
    def __init__(self, min_words: int = 10):
        self.min_words = min_words
        
        self.patterns = {
            'references': r'\[\d+\]|\[citation needed\]|\[note \d+\]',
            'wiki_markup': r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]',
            'html_tags': r'<[^>]+>',
            'urls': r'https?://\S+|www\.\S+',
            'table_markup': r'\{\|.*?\|\}',
            'file_links': r'\[\[(?:File|Image):.+?\]\]',
            'category_links': r'\[\[Category:.+?\]\]',
            'empty_brackets': r'\[\s*\]|\(\s*\)',
            'thumb_sections': r'\|thumb\|.*?(?=\||$)',  
            'multiple_newlines': r'\n\s*\n',
            'multiple_spaces': r' +',
            'vertical_bars': r'\|[^\n]*',  
            'albedo_sections': r'Albedo\|.*?(?=\||$)',  
            'remaining_markup': r'\{\{[^\}]*\}\}|\[\[[^\]]*\]\]',  
            'image_mentions': r'\b(?:figure|illustration|glyph|photo|px|thumbnail|portrait|infobox image)\b', 
            'size_references': r'\b\d{2,4}px\b'  
        }
        
        self.compiled_patterns = {
            name: re.compile(pattern, re.DOTALL | re.IGNORECASE) 
            for name, pattern in self.patterns.items()
        }

    def clean_text(self, text: str) -> Optional[str]:
        if not text or not isinstance(text, str):
            return None

        if text.upper().strip().startswith('#REDIRECT' or '#redirect' or 'redirect' or 'REDIRECT'):
            return None
        cleaned = text
        cleaned = self.compiled_patterns['table_markup'].sub('', cleaned)
        cleaned = self.compiled_patterns['thumb_sections'].sub('', cleaned)
        cleaned = self.compiled_patterns['albedo_sections'].sub('', cleaned)
        cleaned = self.compiled_patterns['vertical_bars'].sub('', cleaned)
        cleaned = self.compiled_patterns['image_mentions'].sub('', cleaned)
        cleaned = self.compiled_patterns['size_references'].sub('', cleaned)
        cleaned = self.compiled_patterns['references'].sub('', cleaned)
        cleaned = self.compiled_patterns['wiki_markup'].sub(r'\1', cleaned)
        cleaned = self.compiled_patterns['html_tags'].sub('', cleaned)
        cleaned = self.compiled_patterns['urls'].sub('', cleaned)
        cleaned = self.compiled_patterns['file_links'].sub('', cleaned)
        cleaned = self.compiled_patterns['category_links'].sub('', cleaned)
        cleaned = self.compiled_patterns['empty_brackets'].sub('', cleaned)
        cleaned = self.compiled_patterns['remaining_markup'].sub('', cleaned)
        cleaned = self.compiled_patterns['multiple_newlines'].sub('\n', cleaned)
        cleaned = self.compiled_patterns['multiple_spaces'].sub(' ', cleaned)
        
        cleaned_lines = [
            line.strip() for line in cleaned.split('\n')
            if line.strip()
            and not any(line.strip().startswith(x) for x in ['|', '{', '}', '==', '[[', ']]', 'thumb|', 'Albedo|'])
            and not any(x in line.strip().lower() for x in ['category:', 'file:', 'image:', '|thumb|', '|albedo|'])
        ]
        
        cleaned = ' '.join(cleaned_lines)
        
        cleaned = cleaned.strip()
        
        word_count = len(cleaned.split())
        if word_count < self.min_words:
            return None
            
        return cleaned

    def clean_title(self, title: str) -> Optional[str]:
        if not title or not isinstance(title, str):
            return None
            
        cleaned = self.compiled_patterns['wiki_markup'].sub(r'\1', title)
        cleaned = self.compiled_patterns['vertical_bars'].sub('', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned if cleaned else None
