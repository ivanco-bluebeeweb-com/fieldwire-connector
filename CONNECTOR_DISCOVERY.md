# Fieldwire Connector — Connector Discovery

**Category:** C47. Construction & Field Service Management  
**Vendor:** Fieldwire  
**Official Website:** https://www.fieldwire.com

## 1. Официальный API
- **Базовый URL API:** `https://api.fieldwire.com/api/v3`
- **Поддерживаемая модель авторизации:** API Token (Authorization: Fieldwire-API-Key <token>)

## 2. Архитектура сущностей
- Ключевые ресурсы платформы Fieldwire:
  - проекты (/projects)
  - строительные задачи (/tasks)
  - планы/чертежи (/sheets)
  - контрольные формы (/forms)

## 3. Требования к отказоустойчивости и безопасности
- Соблюдение вендорных лимитов запросов (Rate Limiting) с экспоненциальной задержкой.
- Строгая валидация Pydantic-схем на входе и выходе каждого запроса.
- Тестовая точка проверки подключения: `GET /api/v3/projects`.
