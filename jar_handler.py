"""
Утилита для работы с .jar файлами модов
"""
import zipfile
from pathlib import Path
from typing import Optional
import tempfile


def extract_jar(jar_path: Path, output_dir: Path) -> Path:
    """
    Распаковывает .jar файл мода
    
    Args:
        jar_path: Путь к .jar файлу
        output_dir: Папка для распаковки
        
    Returns:
        Путь к распакованной папке
    """
    if not jar_path.exists():
        raise FileNotFoundError(f"Файл не найден: {jar_path}")
    
    if not jar_path.suffix.lower() == '.jar':
        raise ValueError(f"Файл не является .jar файлом: {jar_path}")
    
    # Создаем папку для распаковки
    mod_name = jar_path.stem
    extract_path = output_dir / mod_name
    extract_path.mkdir(parents=True, exist_ok=True)
    
    # Распаковываем .jar как zip
    with zipfile.ZipFile(jar_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    return extract_path


def pack_jar(mod_dir: Path, output_jar: Path) -> Path:
    """
    Упаковывает папку мода обратно в .jar файл
    
    Args:
        mod_dir: Путь к папке мода
        output_jar: Путь для сохранения .jar файла
        
    Returns:
        Путь к созданному .jar файлу
    """
    if not mod_dir.exists():
        raise FileNotFoundError(f"Папка не найдена: {mod_dir}")
    
    # Создаем .jar файл
    with zipfile.ZipFile(output_jar, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in mod_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(mod_dir)
                # Убираем файлы подписи, иначе мод может не загрузиться
                if _is_signature_file(arcname):
                    continue
                zipf.write(file_path, arcname)
    
    return output_jar


def _is_signature_file(arcname: Path) -> bool:
    """
    Проверяет, является ли файл подписью JAR.
    Такие файлы нужно удалять после любых правок JAR.
    """
    if len(arcname.parts) == 0:
        return False
    if arcname.parts[0].upper() != "META-INF":
        return False

    upper_name = arcname.name.upper()
    if upper_name.endswith(".SF") or upper_name.endswith(".RSA") or upper_name.endswith(".DSA"):
        return True
    if upper_name.startswith("SIG-"):
        return True

    return False


def translate_jar_mod(jar_path: Path, translator, output_jar: Optional[Path] = None) -> Path:
    """
    Переводит мод прямо из .jar файла
    
    Args:
        jar_path: Путь к .jar файлу мода
        translator: Экземпляр MinecraftModTranslator
        output_jar: Путь для сохранения переведенного .jar (если None, создается рядом)
        
    Returns:
        Путь к переведенному .jar файлу
    """
    
    # Создаем временную папку
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Распаковываем .jar
        print(f"Распаковка {jar_path.name}...")
        extracted = extract_jar(jar_path, temp_path)
        
        # Переводим мод
        print("Перевод мода...")
        translator.translate_mod(str(extracted))
        
        # Определяем путь для сохранения
        if output_jar is None:
            output_jar = jar_path.parent / f"{jar_path.stem}_ru.jar"
        
        # Упаковываем обратно
        print(f"Упаковка в {output_jar.name}...")
        pack_jar(extracted, output_jar)
        
        return output_jar


if __name__ == '__main__':
    import argparse
    from translator import MinecraftModTranslator
    
    parser = argparse.ArgumentParser(description='Работа с .jar файлами модов')
    parser.add_argument('action', choices=['extract', 'pack', 'translate'],
                       help='Действие: extract - распаковать, pack - упаковать, translate - перевести')
    parser.add_argument('input', type=str, help='Входной файл или папка')
    parser.add_argument('-o', '--output', type=str, help='Выходной файл или папка')
    
    args = parser.parse_args()
    
    if args.action == 'extract':
        jar_path = Path(args.input)
        output_dir = Path(args.output) if args.output else jar_path.parent
        extract_path = extract_jar(jar_path, output_dir)
        print(f"Мод распакован в: {extract_path}")
    
    elif args.action == 'pack':
        mod_dir = Path(args.input)
        output_jar = Path(args.output) if args.output else mod_dir.parent / f"{mod_dir.name}.jar"
        pack_jar(mod_dir, output_jar)
        print(f"Мод упакован в: {output_jar}")
    
    elif args.action == 'translate':
        jar_path = Path(args.input)
        translator = MinecraftModTranslator()
        output_jar = Path(args.output) if args.output else None
        result = translate_jar_mod(jar_path, translator, output_jar)
        print(f"Переведенный мод сохранен: {result}")
