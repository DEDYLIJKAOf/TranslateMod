"""
Пример использования переводчика модов Minecraft
"""
from translator import MinecraftModTranslator
from pathlib import Path


def example_translate_mod():
    """Пример перевода мода"""
    
    # Создаем переводчик
    translator = MinecraftModTranslator(source_lang='en', target_lang='ru')
    
    # Путь к моде (замените на реальный путь)
    mod_path = r"C:\Users\konos\AppData\Roaming\.minecraft\mods\example_mod"
    
    # Проверяем существование пути
    if not Path(mod_path).exists():
        print(f"Путь {mod_path} не существует!")
        print("Пожалуйста, укажите правильный путь к моде")
        return
    
    # Переводим мод
    print(f"Начинаем перевод мода: {mod_path}")
    stats = translator.translate_mod(mod_path)
    
    # Выводим статистику
    print("\n" + "="*50)
    print("Статистика перевода:")
    print(f"  Обработано файлов: {stats['files_processed']}")
    print(f"  Переведено строк: {stats['translated']}")
    print(f"  Пропущено строк: {stats['skipped']}")
    print("="*50)


if __name__ == '__main__':
    example_translate_mod()
