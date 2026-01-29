"""
Программа для машинного перевода модов Minecraft на русский язык
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from deep_translator import GoogleTranslator
from tqdm import tqdm


class MinecraftModTranslator:
    """Класс для перевода файлов переводов модов Minecraft"""
    
    def __init__(self, source_lang: str = 'en', target_lang: str = 'ru'):
        """
        Инициализация переводчика
        
        Args:
            source_lang: Исходный язык (по умолчанию английский)
            target_lang: Целевой язык (по умолчанию русский)
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source=source_lang, target=target_lang)
        self.translated_count = 0
        self.skipped_count = 0
        
    def find_lang_files(self, mod_path: Path) -> List[Path]:
        """
        Находит все файлы переводов в моде
        
        Args:
            mod_path: Путь к папке мода
            
        Returns:
            Список путей к файлам переводов
        """
        lang_files = []
        
        # Ищем файлы в стандартных местах:
        # - assets/*/lang/*.json (Forge/Fabric)
        # - lang/*.json (старые моды)
        patterns = [
            '**/assets/*/lang/*.json',
            '**/lang/*.json',
            '**/lang/*.lang',  # старые моды используют .lang
        ]
        
        for pattern in patterns:
            lang_files.extend(mod_path.rglob(pattern))
        
        # Фильтруем только файлы с английским языком или без указания языка
        filtered_files = []
        for file in lang_files:
            if 'en_us.json' in str(file) or 'en_US.json' in str(file) or 'en.json' in str(file):
                filtered_files.append(file)
            elif 'lang' in str(file) and file.suffix == '.json':
                # Если это единственный файл в папке lang, тоже переводим
                parent = file.parent
                if len(list(parent.glob('*.json'))) == 1:
                    filtered_files.append(file)
        
        return filtered_files
    
    def should_translate_value(self, value: str) -> bool:
        """
        Проверяет, нужно ли переводить значение
        
        Args:
            value: Значение для проверки
            
        Returns:
            True если нужно переводить, False иначе
        """
        if not isinstance(value, str):
            return False
        
        # Не переводим пустые строки
        if not value.strip():
            return False
        
        # Не переводим технические строки (цвета, форматирование)
        if value.startswith('§') or value.startswith('&'):
            return False
        
        # Не переводим если это только числа или спецсимволы
        if re.match(r'^[\d\s\W]+$', value):
            return False
        
        # Не переводим очень короткие строки (обычно это коды)
        if len(value.strip()) < 3:
            return False
        
        return True
    
    def translate_text(self, text: str) -> Optional[str]:
        """
        Переводит текст
        
        Args:
            text: Текст для перевода
            
        Returns:
            Переведенный текст или None в случае ошибки
        """
        try:
            # Обрабатываем форматирование Minecraft
            # Сохраняем цветовые коды и форматирование
            translated = self.translator.translate(text)
            return translated
        except Exception as e:
            print(f"\nОшибка при переводе '{text}': {e}")
            return None
    
    def translate_json_file(self, file_path: Path, output_path: Optional[Path] = None) -> bool:
        """
        Переводит JSON файл с переводами
        
        Args:
            file_path: Путь к исходному файлу
            output_path: Путь для сохранения (если None, создается рядом с исходным)
            
        Returns:
            True если перевод успешен, False иначе
        """
        try:
            # Читаем исходный файл
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Определяем путь для сохранения
            if output_path is None:
                # Создаем русскую версию файла
                parent = file_path.parent
                filename = file_path.name
                
                # Заменяем en_us на ru_ru или добавляем ru_ru
                if 'en_us' in filename.lower():
                    filename = filename.lower().replace('en_us', 'ru_ru')
                elif 'en_US' in filename:
                    filename = filename.replace('en_US', 'ru_RU')
                elif 'en.json' in filename.lower():
                    filename = filename.lower().replace('en.json', 'ru_ru.json')
                else:
                    filename = 'ru_ru.json'
                
                output_path = parent / filename
            
            # Переводим данные
            translated_data = {}
            for key, value in tqdm(data.items(), desc=f"Перевод {file_path.name}", leave=False):
                if isinstance(value, str) and self.should_translate_value(value):
                    translated = self.translate_text(value)
                    if translated:
                        translated_data[key] = translated
                        self.translated_count += 1
                    else:
                        translated_data[key] = value
                        self.skipped_count += 1
                else:
                    translated_data[key] = value
            
            # Сохраняем переведенный файл
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"\nОшибка парсинга JSON в файле {file_path}: {e}")
            return False
        except Exception as e:
            print(f"\nОшибка при обработке файла {file_path}: {e}")
            return False
    
    def translate_mod(self, mod_path: str, output_path: Optional[str] = None) -> Dict[str, int]:
        """
        Переводит все файлы переводов в моде
        
        Args:
            mod_path: Путь к папке мода
            output_path: Путь для сохранения (если None, сохраняется рядом с исходным)
            
        Returns:
            Словарь со статистикой перевода
        """
        mod_path = Path(mod_path)
        if not mod_path.exists():
            raise ValueError(f"Путь к моде не существует: {mod_path}")
        
        # Сбрасываем счетчики
        self.translated_count = 0
        self.skipped_count = 0
        
        # Находим все файлы переводов
        lang_files = self.find_lang_files(mod_path)
        
        if not lang_files:
            print(f"Файлы переводов не найдены в {mod_path}")
            return {
                'translated': 0,
                'skipped': 0,
                'files_processed': 0
            }
        
        print(f"Найдено {len(lang_files)} файлов переводов")
        
        # Переводим каждый файл
        for lang_file in tqdm(lang_files, desc="Обработка файлов"):
            if output_path:
                # Если указан выходной путь, сохраняем туда с сохранением структуры
                relative_path = lang_file.relative_to(mod_path)
                output_file = Path(output_path) / relative_path
                self.translate_json_file(lang_file, output_file)
            else:
                self.translate_json_file(lang_file)
        
        return {
            'translated': self.translated_count,
            'skipped': self.skipped_count,
            'files_processed': len(lang_files)
        }


def main():
    """Главная функция для запуска из командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Переводчик модов Minecraft на русский язык'
    )
    parser.add_argument(
        'mod_path',
        type=str,
        help='Путь к папке мода или .jar файлу мода'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Путь для сохранения переведенных файлов (по умолчанию рядом с исходными)'
    )
    parser.add_argument(
        '--source-lang',
        type=str,
        default='en',
        help='Исходный язык (по умолчанию: en)'
    )
    parser.add_argument(
        '--target-lang',
        type=str,
        default='ru',
        help='Целевой язык (по умолчанию: ru)'
    )
    
    args = parser.parse_args()
    
    mod_path = Path(args.mod_path)
    
    # Проверяем, является ли входной файл .jar
    if mod_path.is_file() and mod_path.suffix.lower() == '.jar':
        print("Обнаружен .jar файл, используем автоматическую обработку...")
        try:
            from jar_handler import translate_jar_mod
            
            translator = MinecraftModTranslator(
                source_lang=args.source_lang,
                target_lang=args.target_lang
            )
            
            output_jar = Path(args.output) if args.output else None
            result_jar = translate_jar_mod(mod_path, translator, output_jar)
            
            print("\n" + "="*50)
            print("Перевод завершен!")
            print(f"Переведенный мод сохранен: {result_jar}")
            print("="*50)
            return
        except ImportError:
            print("Ошибка: не удалось импортировать jar_handler")
            print("Убедитесь, что файл jar_handler.py находится в той же папке")
            return
    
    # Создаем переводчик
    translator = MinecraftModTranslator(
        source_lang=args.source_lang,
        target_lang=args.target_lang
    )
    
    # Переводим мод
    print(f"Начинаем перевод мода: {args.mod_path}")
    stats = translator.translate_mod(args.mod_path, args.output)
    
    # Выводим статистику
    print("\n" + "="*50)
    print("Статистика перевода:")
    print(f"  Обработано файлов: {stats['files_processed']}")
    print(f"  Переведено строк: {stats['translated']}")
    print(f"  Пропущено строк: {stats['skipped']}")
    print("="*50)


if __name__ == '__main__':
    main()
