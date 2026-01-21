import torch
import whisper
import os
import glob
import time
from pydub import AudioSegment
from pydub.utils import make_chunks

print("=" * 70)
print("🎯 АУДИО -> ТЕКСТ + ПРОМПТ ДЛЯ КОНСПЕКТИРОВАНИЯ")
print("=" * 70)

# Засекаем общее время работы
total_start_time = time.time()

# Автоматически используем GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Устройство: {device}")

# Папка скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Папка: {script_dir}")

# Выбор модели (по умолчанию 5 - large)
print("\n🤖 ВЫБОР МОДЕЛИ WHISPER:")
print("1. tiny (слабая) - быстрая, низкое качество")
print("2. base (нормальная) - баланс скорости/качества") 
print("3. small (хорошая) - хорошее качество, умеренная скорость")
print("4. medium (отличная) - высокое качество, медленная")
print("5. large (лучшая) - максимальное качество, очень медленная")

model_choice = input("Выберите модель (1-5, по умолчанию 5): ").strip() or "5"

model_map = {
    "1": "tiny",
    "2": "base", 
    "3": "small",
    "4": "medium",
    "5": "large"
}

selected_model = model_map.get(model_choice, "large")
print(f"✅ Выбрана модель: {selected_model}")

# Выбор контекста (по умолчанию 1 - включен)
print("\n🔄 ВЫБОР КОНТЕКСТА:")
print("0. Без контекста - каждый сегмент обрабатывается независимо")
print("1. С контекстом - учитывается предыдущий текст (лучшее качество)")

context_choice = input("Выберите режим (0-1, по умолчанию 1): ").strip() or "1"
use_context = context_choice != "0"
print(f"✅ Режим контекста: {'ВКЛ' if use_context else 'ВЫКЛ'}")

# Поиск аудиофайлов
audio_extensions = ['*.m4a', '*.mp3', '*.wav', '*.mp4', '*.ogg', '*.flac', '*.aac', '*.m4b']
audio_files = []

for ext in audio_extensions:
    audio_files.extend(glob.glob(ext))
    audio_files.extend(glob.glob(ext.upper()))

# Удаляем дубликаты
audio_files = list(set(audio_files))

if not audio_files:
    print("Аудиофайлы не найдены!")
    exit()

print(f"Найдено файлов: {len(audio_files)}")
for file in audio_files:
    file_size = os.path.getsize(file) / (1024 * 1024)
    print(f"  - {os.path.basename(file)} ({file_size:.1f} MB)")

# Загрузка выбранной модели
print(f"\n🔄 Загрузка модели Whisper {selected_model}...")
model_load_start = time.time()
model = whisper.load_model(selected_model, device=device)
model_load_time = time.time() - model_load_start
print(f"✅ Модель '{selected_model}' загружена за {model_load_time:.1f} сек")

def split_audio_with_overlap(file_path, segment_length_ms=70000, overlap_ms=10000):  # 1:10 минут с захлестом 10 сек
    """Разбивает аудиофайл на сегменты с захлестом"""
    print(f"✂️  Разбиваем аудио на сегменты {segment_length_ms/60000:.1f} мин с захлестом {overlap_ms/1000} сек...")
    
    try:
        # Загружаем аудиофайл
        audio = AudioSegment.from_file(file_path)
        duration_ms = len(audio)
        duration_sec = duration_ms / 1000
        print(f"   Длительность оригинала: {duration_sec/60:.1f} минут")
        
        # Создаем папку для сегментов
        base_name = os.path.splitext(file_path)[0]
        segments_dir = f"{base_name}_segments"
        os.makedirs(segments_dir, exist_ok=True)
        
        segments_info = []
        step_ms = segment_length_ms - overlap_ms  # Шаг между началами сегментов
        
        i = 0
        start_ms = 0
        
        while start_ms < duration_ms:
            end_ms = min(start_ms + segment_length_ms, duration_ms)
            
            # Извлекаем сегмент
            chunk = audio[start_ms:end_ms]
            
            # Сохраняем сегмент
            chunk_name = f"{base_name}_part{i+1:03d}.wav"
            chunk_path = os.path.join(segments_dir, chunk_name)
            chunk.export(chunk_path, format="wav")
            
            segments_info.append({
                'path': chunk_path,
                'start': start_ms / 1000,
                'end': end_ms / 1000,
                'index': i + 1
            })
            
            # Переходим к следующему сегменту
            start_ms += step_ms
            i += 1
            
            # Если оставшийся фрагмент слишком короткий, объединяем с предыдущим
            if duration_ms - start_ms < overlap_ms and i > 0:
                break
        
        print(f"✅ Создано сегментов с захлестом: {len(segments_info)}")
        
        # Выводим информацию о сегментах
        for seg in segments_info:
            start_min = int(seg['start'] // 60)
            start_sec = int(seg['start'] % 60)
            end_min = int(seg['end'] // 60)
            end_sec = int(seg['end'] % 60)
            print(f"   {start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}")
            
        return segments_info, duration_sec
        
    except Exception as e:
        print(f"❌ Ошибка при разбивке аудио: {e}")
        return [], 0

def transcribe_segment(segment_path, segment_index, total_segments):
    """Транскрибирует один сегмент аудио"""
    print(f"   🎧 Сегмент {segment_index}/{total_segments}...")
    
    try:
        result = model.transcribe(
            segment_path,
            language="ru",
            fp16=(device == "cuda"),
            temperature=0.0,
            best_of=3,
            beam_size=3,
            no_speech_threshold=0.6,
            condition_on_previous_text=use_context  # Используем выбранный режим контекста
        )
        
        text = result["text"].strip()
        return text
        
    except Exception as e:
        print(f"❌ Ошибка транскрибации сегмента {segment_index}: {e}")
        return ""

def create_ai_prompt(filename, total_duration, total_segments, lecture_text):
    """Создает промпт для AI с текстом лекции"""
    
    prompt = f"""ПРОМПТ ДЛЯ КОНСПЕКТИРОВАНИЯ ЛЕКЦИИ

ИНФОРМАЦИЯ О ЛЕКЦИИ:
- Файл: {filename}
- Длительность: {total_duration/60:.1f} минут
- Сегментов: {total_segments}

ЗАДАНИЕ:
Проанализируй предоставленный текст лекции и создай структурированный конспект. Текст содержит транскрипцию университетской лекции.
Так как текст обрабатывался автоматически то в нем есть искажения слов.
Нужно записать эту лекцию в том порядке в котором идет лекция.
все это оформить для приложения obsidian.


ТЕКСТ ЛЕКЦИИ ДЛЯ АНАЛИЗА:
{lecture_text}

КОНЕЦ ТЕКСТА ЛЕКЦИИ
"""
    return prompt

# Обработка файлов
successful_files = 0

for audio_file in audio_files:
    filename = os.path.basename(audio_file)
    file_size = os.path.getsize(audio_file) / (1024 * 1024)
    
    print(f"\n🎯 Обработка: {filename} ({file_size:.1f} MB)")
    print("=" * 50)
    
    start_time = time.time()
    
    # 1. Разбиваем аудио на сегменты С ЗАХЛЕСТОМ
    segments_info, total_duration = split_audio_with_overlap(audio_file)
    
    if not segments_info:
        print("❌ Не удалось разбить аудио на сегменты")
        continue
    
    # 2. Транскрибируем каждый сегмент
    all_transcriptions = []
    full_lecture_text = ""
    
    for i, segment in enumerate(segments_info):
        start_min = int(segment['start'] // 60)
        start_sec = int(segment['start'] % 60)
        end_min = int(segment['end'] // 60)
        end_sec = int(segment['end'] % 60)
        
        progress = f"[{i+1}/{len(segments_info)}]"
        
        print(f"   {progress} {start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}")
        
        segment_text = transcribe_segment(segment['path'], i+1, len(segments_info))
        
        if segment_text:
            segment_header = f"\n--- СЕГМЕНТ {i+1} ({start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}) ---\n"
            formatted_segment = segment_header + segment_text + "\n"
            all_transcriptions.append(formatted_segment)
            full_lecture_text += segment_text + " "
        
        # Очистка памяти GPU между сегментами
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    # 3. Создаем промпт для AI
    base_name = os.path.splitext(audio_file)[0]
    output_file = f"{base_name}_для_конспекта.md"
    
    ai_prompt = create_ai_prompt(filename, total_duration, len(segments_info), full_lecture_text)
    
    # 4. Сохраняем все в файл
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ai_prompt)
        
        # Дополнительно сохраняем полную транскрипцию в отдельный файл
        transcript_file = f"{base_name}_полная_транскрипция.md"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write("# ПОЛНАЯ ТРАНСКРИПЦИЯ ЛЕКЦИИ\n\n")
            f.writelines(all_transcriptions)
        
        processing_time = time.time() - start_time
        
        # Статистика
        total_text_length = len(full_lecture_text)
        
        print(f"\n✅ Файл обработан за {processing_time:.1f} сек")
        print(f"📄 Созданы файлы:")
        print(f"   - {output_file} (промпт для AI)")
        print(f"   - {transcript_file} (полная транскрипция)")
        print(f"📝 Общий текст: {total_text_length} символов")
        print(f"⏱️  Время на минуту аудио: {processing_time/(total_duration/60):.1f} сек/мин")
        
        # Показываем следующий шаг
        print(f"\n🎯 СЛЕДУЮЩИЙ ШАГ:")
        print(f"   Скопируй содержимое файла '{output_file}'")
        print(f"   И отправь мне - я создам структурированный конспект!")
        
        successful_files += 1
        
        # Удаляем временные сегменты
        import shutil
        segments_dir = f"{base_name}_segments"
        if os.path.exists(segments_dir):
            shutil.rmtree(segments_dir)
            print("🧹 Временные файлы сегментов удалены")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении файла: {e}")

# Итоговая статистика
total_time = time.time() - total_start_time
print("\n" + "=" * 70)
print("📊 ИТОГОВЫЙ ОТЧЕТ")
print("=" * 70)
print(f"🕒 Общее время работы: {total_time:.1f} сек ({total_time/60:.1f} мин)")
print(f"⏱️  Время загрузки модели: {model_load_time:.1f} сек")
print(f"🤖 Использованная модель: {selected_model}")
print(f"🔄 Режим контекста: {'ВКЛ' if use_context else 'ВЫКЛ'}")
print(f"📁 Обработано файлов: {successful_files}/{len(audio_files)}")

if successful_files > 0:
    print(f"\n🎯 РЕЖИМ ОБРАБОТКИ:")
    print(f"   • Разбивка на сегменты по 1:10 минут с захлестом 10 сек")
    print(f"   • Сегменты: 00:00-1:10, 01:00-2:10, 02:00-3:10 и т.д.")
    print(f"   • Модель: Whisper {selected_model}")
    print(f"   • Контекст: {'ВКЛ' if use_context else 'ВЫКЛ'}")
    print(f"   • Выходные файлы:")
    print(f"     - _для_конспекта.md - промпт для AI")
    print(f"     - _полная_транскрипция.md - сырой текст")

print("\n💡 ИНСТРУКЦИЯ:")
print("   1. Открой файл с суффиксом '_для_конспекта.md'")
print("   2. Скопируй ВЕСЬ его содержимое")
print("   3. Отправь мне скопированный текст")
print("   4. Я проанализирую лекцию и создам структурированный конспект!")

print("=" * 70)
print("Обработка завершена! Жду промпт для конспектирования! 🎓")
input("Нажмите Enter для выхода...")