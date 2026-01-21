package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

// Структура для хранения метаданных найденного вхождения
type Match struct {
	FilePath string
	LineNum  int
	Content  string
}

func main() {
	const targetDir = "./logs"
	const query = "ERROR"

	files, err := os.ReadDir(targetDir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Ошибка доступа к директории: %v\n", err)
		os.Exit(1)
	}

	matchChan := make(chan Match) // Канал для результатов
	var wg sync.WaitGroup

	// Итерация по файлам и запуск горутин
	for _, f := range files {
		if f.IsDir() || !strings.HasSuffix(f.Name(), ".txt") {
			continue
		}

		wg.Add(1)
		go func(fileName string) {
			defer wg.Done()
			searchInFile(filepath.Join(targetDir, fileName), query, matchChan)
		}(f.Name())
	}

	// Горутина-монитор для закрытия канала
	go func() {
		wg.Wait()
		close(matchChan)
	}()

	// Сбор результатов (Consumer)
	fmt.Printf("Результаты поиска [Запрос: %s]:\n", query)
	fmt.Println(strings.Repeat("-", 50))

	for m := range matchChan {
		fmt.Printf("%s:%d | %s\n", m.FilePath, m.LineNum, m.Content)
	}
}

func searchInFile(path string, query string, ch chan<- Match) {
	file, err := os.Open(path)
	if err != nil {
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	lineIdx := 1
	for scanner.Scan() {
		line := scanner.Text()
		if strings.Contains(line, query) {
			ch <- Match{
				FilePath: path,
				LineNum:  lineIdx,
				Content:  strings.TrimSpace(line),
			}
		}
		lineIdx++
	}
}
