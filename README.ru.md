<div align="center">

# PrincessTorr

[🇺🇸 English](README.md) | 🇷🇺 Русский

*Аддон для Kodi: каталог фильмов и сериалов из TMDb, поиск раздач по требованию и воспроизведение через Jacktorr/TorrServer. UI нативный, внешний вид задаёт установленный скин.*

[![Kodi Version](https://img.shields.io/badge/Kodi-21+-blue.svg)](https://kodi.tv)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---
</div>

## Возможности

- Каталог TMDb с локализованными метаданными (по умолчанию русский): фильмы, сериалы, жанры, поиск.
- Поиск раздач по требованию, источник JacRed (публичный агрегатор RU-трекеров, как в Lampa) или Prowlarr.
- Озвучка прямо в строке раздачи, плюс качество, размер, сиды.
- Сортировка и фильтры списка: сиды/размер/качество, только русский, поиск по слову.
- Выбор вида списка (постеры, стена и т.п.) через контекстное меню "Сделать вид стандартным" запоминается отдельно для фильмов и сериалов.
- Статус выхода серий: невышедшие помечены и показывают дату выхода.
- Продолжить просмотр и локальная история.
- Запуск через Jacktorr. Поиск стартует только при открытии фильма или серии, поэтому каталог открывается быстро.

## Установка

### Из репозитория (рекомендуется, авто-обновления)

Страница репозитория: https://maxivimax.github.io/PrincessTorr/

1. Kodi → Settings → System → Add-ons → включи **Unknown sources** (неизвестные источники).
2. Скачай zip репозитория:
   [`repository.princesstorr-1.0.0.zip`](https://maxivimax.github.io/PrincessTorr/repository.princesstorr/repository.princesstorr-1.0.0.zip).
3. Add-ons → **Install from zip file** → выбери скачанный zip.
4. Add-ons → **Install from repository** → *PrincessTorr Repository* → Video add-ons → PrincessTorr.

Дальше Kodi обновляет аддон автоматически.

### Вручную (одним zip)

1. Скопируй папку `plugin.video.princesstorr` в каталог аддонов Kodi
   (`~/.kodi/addons/` на Linux, `%APPDATA%\Kodi\addons\` на Windows) или поставь собранный zip через "Установка из ZIP".
2. Запусти Kodi, аддон появится в разделе "Видео".

В обоих случаях установи и настрой [`plugin.video.jacktorr`](https://github.com/Sam-Max/plugin.video.jacktorr) на свой TorrServer.

## Настройка

Настройки аддона:

- TMDb: [API ключ (v3 или v4 Bearer)](https://www.themoviedb.org/settings/api), язык метаданных.
- Источник поиска: JacRed (по умолчанию) или Prowlarr с адресом и ключом.
- Сеть: при необходимости HTTP-прокси.

Если TMDb недоступен из-за блокировки по DNS, помогает чистый DNS на устройстве (например Quad9 через Private DNS).

## Структура меню

```
Фильмы: Популярное / Сейчас смотрят / Новинки / По жанрам / Поиск
Сериалы: Популярное / В эфире / По жанрам / Поиск
```

Открытие фильма запускает поиск раздач. Сериал ведёт к сезонам и сериям; у сезона есть действие в контекстном меню "Найти раздачи на весь сезон".

## Зависимости

Только стандартная библиотека Python (urllib). Внешних модулей нет.

## Автор

Telegram [@iamprincessshine](https://t.me/iamprincessshine)
