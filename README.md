# <img src="images\rt-key.png" alt="Ростелеком Ключ" width="100"> rt-key
# Ростелеком Ключ (RT-Key) — Custom Component for Home Assistant

[![HACS Validation](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2026.7%2B-blue.svg)](https://www.home-assistant.io/)

Кастомная интеграция **Ростелеком Ключ** (`key.rt.ru`) для **Home Assistant**, распространяемая через **HACS**. 

Позволяет управлять умными домофонами, видеокамерами прямо из Home Assistant.

---

## 🚀 Возможности

- **🔑 Умные Домофоны (`lock.py`)**: Открытие дверей подъезда и калиток из HA.
- **📹 Видеонаблюдение (`camera.py`)**: видеопотоки с камер домофонов и двора.
- **🔘 Быстрые Кнопки (`button.py`)**: Элементы `button.open_door` и `button.open_barrier` для вызова в 1 клик.
- **🌐 Авторизация по паролю или Токену (`config_flow.py`)**: Интерактивная настройка по паролю или прямого ввода Bearer Token.

---

## 📥 Установка через HACS

1. Откройте **HACS** в Home Assistant.
2. Перейдите в раздел **Integrations** (Интеграции).
3. В правом верхнем углу нажмите **⋮** -> **Custom repositories** (Пользовательские репозитории).
4. Добавьте URL репозитория: `https://github.com/Nikolailavr/RT-key`
5. Выберите категорию: **Integration** (Интеграция) и нажмите **Add**.
6. Найдите **Ростелеком Ключ** в поиске и нажмите **Download** (Скачать).
7. Перезапустите Home Assistant.

---

## ⚙️ Настройка

1. Перейдите в **Настройки** -> **Устройства и службы** -> **Добавить интеграцию**.
2. Введите в поиске **Ростелеком Ключ**.
3. Выберите метод входа:
   - **По паролю**: Введите номер телефона (`+79XXXXXXXXX`) и пароль от личного кабинета Ростелеком ключ
   - **SMS**: Введите номер телефона (`+79XXXXXXXXX`) и код из СМС. (Временно не работает)
   - **Token**: Введите скопированный Bearer Token.

---

## 📜 Лицензия
MIT
