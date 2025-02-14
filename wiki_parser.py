import bz2
import json
import mwparserfromhell
import xml.etree.ElementTree as ET
import re
import time

class WikipediaParser:
    def __init__(self, dump_path: str, output_path: str):
        self.dump_path = dump_path
        self.output_path = output_path
        self.processed_count = 0

    def parse_dump(self):
        print("Starting to parse Wikipedia dump...")
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('[\n')

        dump_file = bz2.BZ2File(self.dump_path)
        context = ET.iterparse(dump_file, events=('end',))

        first_article = True
        last_report_time = time.time()
        start_time = time.time()

        try:
            for event, elem in context:
                if self.strip_ns(elem.tag) == 'page':
                    article = self._process_page(elem)
                    if article:
                        with open(self.output_path, 'a', encoding='utf-8') as f:
                            if not first_article:
                                f.write(',\n')
                            json.dump(article, f, ensure_ascii=False)
                            first_article = False
                            self.processed_count += 1

                        current_time = time.time()
                        if current_time - last_report_time >= 5:
                            elapsed = current_time - start_time
                            rate = self.processed_count / elapsed
                            print(f"\rProcessed {self.processed_count:,} articles ({rate:.1f} articles/sec)", end='')
                            last_report_time = current_time

                    elem.clear()

        except KeyboardInterrupt:
            print("\nkeyboard interrupt...")
        finally:
            with open(self.output_path, 'a', encoding='utf-8') as f:
                f.write('\n]')

            elapsed = time.time() - start_time
            rate = self.processed_count / elapsed
            print(f"\nFinished! Processed {self.processed_count:,} articles in {elapsed:.1f} seconds")
            print(f"Average rate: {rate:.1f} articles/sec")

    def _process_page(self, page_elem: ET.Element):
        ns = page_elem.find(self.with_ns('ns'))
        if ns is None or ns.text != '0':
            return None

        title = page_elem.find(self.with_ns('title'))
        revision = page_elem.find(self.with_ns('revision'))
        if title is None or revision is None:
            return None

        text = revision.find(self.with_ns('text'))
        if text is None or not text.text:
            return None

        try:
            if text.text.upper().startswith('#REDIRECT'):
                return None

            wikicode = mwparserfromhell.parse(text.text)
            clean_text = self._clean_content(wikicode)

            if clean_text and len(clean_text) > 50: 
                return {'title': title.text, 'text': clean_text}
        except Exception:
            pass
        return None

    def _clean_content(self, wikicode):
        try:
            code = wikicode.strip_code()
            code = re.sub('<!--.*?-->', '', code, flags=re.DOTALL)
            code = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', '', code)
            code = re.sub(r'\[https?:[^\]]*\]', '', code)
            code = re.sub(r'\[\/\/[^\]]*\]', '', code)
            code = re.sub(r'https?://\S+', '', code)
            code = re.sub(r'www\.\S+', '', code)
            code = re.sub(r'\[\s*\]', '', code)
            code = re.sub(r'\(\s*\)', '', code)
            code = re.sub(r'\n\s*\n', '\n\n', code)

            lines = [line.strip() for line in code.split('\n')
                    if line.strip() 
                    and not line.strip().startswith('|')
                    and not line.strip().startswith('{')
                    and not line.strip().startswith('}')
                    and not line.strip().startswith('[[')
                    and not line.strip().startswith('Category:')
                    and not line.strip().startswith('File:')
                    and not line.strip().startswith('Image:')]
            
            text = '\n'.join(lines)
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'^\W+|\W+$', '', text, flags=re.MULTILINE)

            cleaned = text.strip()
            if len(cleaned) > 50:
                return cleaned
            return None
        except Exception:
            return None

    def strip_ns(self, tag):
        return tag.split('}')[-1]

    def with_ns(self, tag):
        return f"{{http://www.mediawiki.org/xml/export-0.11/}}{tag}"

