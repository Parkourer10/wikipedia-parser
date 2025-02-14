import json
from wiki_parser import WikipediaParser
from clean import WikipediaTextCleaner
from processing import TextProcessor
import time
import bz2
import xml.etree.ElementTree as ET


def load_config(config_path='config.txt'):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = {}
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
            
            if 'dump_path' not in config or 'output_path' not in config:
                raise ValueError("Config must specify both dump_path and output_path")
                
            return config
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{config_path}' not found")

def process_wikipedia_pipeline(dump_path: str, output_path: str):
    print("Starting Wikipedia processing pipeline...")
    
    parser = WikipediaParser(dump_path, "temp.json")
    cleaner = WikipediaTextCleaner(min_words=10)
    processor = TextProcessor()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('[\n')
    
    processed_count = 0
    start_time = time.time()
    last_time = start_time
    last_count = 0
    first_article = True
    
    try:
        dump_file = bz2.BZ2File(dump_path)
        context = ET.iterparse(dump_file, events=('end',))

        for _, elem in context:
            if parser.strip_ns(elem.tag) == 'page':
                try:
                    article = parser._process_page(elem)
                    if article:
                        cleaned_text = cleaner.clean_text(article['text'])
                        cleaned_title = cleaner.clean_title(article['title'])
                        
                        if cleaned_text and cleaned_title:
                            processed_text = processor.process_text(cleaned_text)
                            
                            if processed_text:
                                output_article = {
                                    'title': cleaned_title,
                                    'text': processed_text
                                }
                                
                                with open(output_path, 'a', encoding='utf-8') as f:
                                    if not first_article:
                                        f.write(',\n')
                                    json.dump(output_article, f, ensure_ascii=False)
                                    first_article = False
                                
                                processed_count += 1
                                
                                current_time = time.time()
                                total_elapsed = current_time - start_time
                                batch_elapsed = current_time - last_time
                                
                                batch_count = processed_count - last_count
                                instant_rate = batch_count / batch_elapsed if batch_elapsed > 0 else 0
                                
                                avg_rate = processed_count / total_elapsed if total_elapsed > 0 else 0
                                
                                if processed_count % 100 == 0:
                                    print(f"\rProcessed {processed_count:,} articles (Current: {instant_rate:.1f} art/s, Avg: {avg_rate:.1f} art/s)", end='')
                                
                                last_time = current_time
                                last_count = processed_count
                    
                except Exception as e:
                    continue
                finally:
                    elem.clear()
                    
    except KeyboardInterrupt:
        print("\nInterrupted by user...")
    finally:
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write('\n]')
        
        elapsed = time.time() - start_time
        rate = processed_count / elapsed if elapsed > 0 else 0
        print(f"\nFinished! Processed {processed_count:,} articles in {elapsed:.1f} seconds")
        print(f"Average rate: {rate:.1f} articles/sec")

def main():
    config = load_config()
    process_wikipedia_pipeline(
        config["dump_path"],
        config["output_path"]
    )

if __name__ == "__main__":
    main()