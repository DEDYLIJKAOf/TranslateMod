## Пошаговая инструкция по использованию

### 1. Установка зависимостей
1. Открой `E:\ModTranslate`.
2. Запусти `install.bat` (двойной клик).

Если хочешь через консоль:
```
py -m pip install -r E:\ModTranslate\requirements.txt
```

### 1.1. GUI (окно)
Запусти:
```
py E:\ModTranslate\gui.py
```
или двойным кликом по `gui.bat`.

### 2. Перевод мода из .jar
1. Убедись, что мод лежит в `mods` или укажи полный путь к файлу.
2. Запусти перевод:
```
py E:\ModTranslate\translator.py "E:\MultiMC\instances\1.20.1\.minecraft\mods\hexcasting-forge-1.20.1-0.11.3.jar"
```
3. Жди окончания. Перевод занимает время.
4. Появится файл:
```
E:\MultiMC\instances\1.20.1\.minecraft\mods\hexcasting-forge-1.20.1-0.11.3_ru.jar
```

### 3. Важно про моды
В папке `mods` должен быть только **один** jar каждого мода.
После перевода:
- удали оригинальный `.jar`
- оставь только `*_ru.jar`

### 4. Перевод мода из папки
Если мод распакован в папку:
```
py E:\ModTranslate\translator.py "E:\путь\к\папке\мода"
```
Файл `ru_ru.json` появится рядом с `en_us.json`.

### 5. Проверка перевода внутри .jar
Можно убедиться, что в моде есть `ru_ru.json`:
```
py -c "import zipfile; p=r'E:\MultiMC\instances\1.20.1\.minecraft\mods\hexcasting-forge-1.20.1-0.11.3_ru.jar'; z=zipfile.ZipFile(p); print([n for n in z.namelist() if n.endswith('lang/ru_ru.json')])"
```

### 6. Если игра не запускается после перевода
1. Убери `*_ru.jar` из `mods`.
2. Запусти игру.
3. Если запуск восстановился — проблема в переведённом файле.
4. Сообщи мне — я помогу поправить переводчик под этот мод.
