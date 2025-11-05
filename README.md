# MCP Atlassian

![PyPI Version](https://img.shields.io/pypi/v/mcp-atlassian)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-atlassian)
![PePy - Total Downloads](https://static.pepy.tech/personalized-badge/mcp-atlassian?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)
[![Run Tests](https://github.com/sooperset/mcp-atlassian/actions/workflows/tests.yml/badge.svg)](https://github.com/sooperset/mcp-atlassian/actions/workflows/tests.yml)
![License](https://img.shields.io/github/license/sooperset/mcp-atlassian)
[![Docs](https://img.shields.io/badge/docs-mintlify-blue)](https://personal-1d37018d.mintlify.app)

Model Context Protocol (MCP) server for Atlassian products (Confluence and Jira). Supports both Cloud and Server/Data Center deployments.

https://github.com/user-attachments/assets/35303504-14c6-4ae4-913b-7c25ea511c3e

<details>
<summary>Confluence Demo</summary>

https://github.com/user-attachments/assets/7fe9c488-ad0c-4876-9b54-120b666bb785

</details>

## Quick Start

| Product        | Deployment Type    | Support Status              |
|----------------|--------------------|-----------------------------|
| **Confluence** | Cloud              | ✅ Fully supported           |
| **Confluence** | Server/Data Center | ✅ Supported (version 6.0+)  |
| **Jira**       | Cloud              | ✅ Fully supported           |
| **Jira**       | Server/Data Center | ✅ Supported (version 8.14+) |
| **Jira**       | Server 6.3.15      | ✅ Supported (legacy mode)   |

### 1. Get Your API Token

Go to https://id.atlassian.com/manage-profile/security/api-tokens and create a token.

> For Server/Data Center, use a Personal Access Token instead. See [Authentication](https://personal-1d37018d.mintlify.app/docs/authentication).

### 2. Configure Your IDE

Add to your Claude Desktop or Cursor MCP configuration:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_api_token",
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

> **Python 3.14 not yet supported.** Use `["--python=3.12", "mcp-atlassian"]` as args if needed.

> **Server/Data Center users**: Use `JIRA_PERSONAL_TOKEN` instead of `JIRA_USERNAME` + `JIRA_API_TOKEN`. See [Authentication](https://personal-1d37018d.mintlify.app/docs/authentication) for details.

### 3. Start Using

Ask your AI assistant to:
- **"Find issues assigned to me in PROJ project"**
- **"Search Confluence for onboarding docs"**
- **"Create a bug ticket for the login issue"**
- **"Update the status of PROJ-123 to Done"**

## Documentation

Full documentation is available at **[personal-1d37018d.mintlify.app](https://personal-1d37018d.mintlify.app)**.

Documentation is also available in [llms.txt format](https://llmstxt.org/), which LLMs can consume easily:
- [`llms.txt`](https://personal-1d37018d.mintlify.app/llms.txt) — documentation sitemap
- [`llms-full.txt`](https://personal-1d37018d.mintlify.app/llms-full.txt) — complete documentation

| Topic | Description |
|-------|-------------|
| [Installation](https://personal-1d37018d.mintlify.app/docs/installation) | uvx, Docker, pip, from source |
| [Authentication](https://personal-1d37018d.mintlify.app/docs/authentication) | API tokens, PAT, OAuth 2.0 |
| [Configuration](https://personal-1d37018d.mintlify.app/docs/configuration) | IDE setup, environment variables |
| [HTTP Transport](https://personal-1d37018d.mintlify.app/docs/http-transport) | SSE, streamable-http, multi-user |
| [Tools Reference](https://personal-1d37018d.mintlify.app/docs/tools-reference) | All Jira & Confluence tools |
| [Troubleshooting](https://personal-1d37018d.mintlify.app/docs/troubleshooting) | Common issues & debugging |

## Compatibility

| Product | Deployment | Support |
|---------|------------|---------|
| Confluence | Cloud | Fully supported |
| Confluence | Server/Data Center | Supported (v6.0+) |
| Jira | Cloud | Fully supported |
| Jira | Server/Data Center | Supported (v8.14+) |

## Key Tools

| Jira | Confluence |
|------|------------|
| `jira_search` - Search with JQL | `confluence_search` - Search with CQL |
| `jira_get_issue` - Get issue details | `confluence_get_page` - Get page content |
| `jira_create_issue` - Create issues | `confluence_create_page` - Create pages |
| `jira_update_issue` - Update issues | `confluence_update_page` - Update pages |
| `jira_transition_issue` - Change status | `confluence_add_comment` - Add comments |
| `jira_get_issue_sla` - Calculate SLA metrics | `confluence_get_page_views` - Get page view stats (Cloud only) |

See [Tools Reference](https://personal-1d37018d.mintlify.app/docs/tools-reference) for the complete list.

**Linux:**
```bash
# Логи обычно в ~/.cache или ~/.local/share/Claude/logs/
find ~ -name "mcp*.log" -type f 2>/dev/null
```

#### Просмотр исключений и ошибок

**Включить детальное логирование исключений:**
```bash
# Максимальная детализация с трассировкой стека
MCP_VERY_VERBOSE=true docker run --rm -i mcp-atlassian:latest
```

**Типичные ошибки и решения:**

1. **Ошибка аутентификации:**
   ```
   ERROR - mcp-atlassian - Authentication failed for Jira API (401)
   ```
   - Проверьте правильность `JIRA_USERNAME` и `JIRA_PASSWORD`
   - Убедитесь, что пользователь имеет права на API доступ

2. **Ошибка SSL сертификата:**
   ```
   ERROR - mcp-atlassian - SSL certificate verification failed
   ```
   - Установите `JIRA_CA_FILE` с путем к CA bundle
   - Или временно `JIRA_TLS_INSECURE=true` (только для тестирования)

3. **Ошибка подключения:**
   ```
   ERROR - mcp-atlassian - Network or API Error
   ```
   - Проверьте доступность `JIRA_URL`
   - Проверьте настройки прокси, если используются

#### Отладка проблем

**1. Включите максимальную детализацию в конфигурации IDE:**

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "MCP_VERY_VERBOSE=true",
        "-e", "MCP_LOGGING_STDOUT=true",
        "mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://jira.example.com",
        "JIRA_USERNAME": "admin",
        "JIRA_PASSWORD": "password"
      }
    }
  }
}
```

**2. Проверьте логи инициализации:**

Ищите в логах строки:
- `DEBUG - mcp-atlassian - Logging level set to: DEBUG`
- `INFO - mcp-atlassian - Jira authentication successful`
- `WARNING - mcp-atlassian - ...` (предупреждения)
- `ERROR - mcp-atlassian - ...` (ошибки)

**3. Маскирование чувствительных данных:**

В логах автоматически маскируются:
- Токены аутентификации (показываются только первые/последние 4 символа)
- Пароли
- Cookie значения
- Proxy credentials

Пример:
```
DEBUG - mcp-jira - Authorization: Basic YWRt****word
```

**4. Проверка конфигурации Server 6.x:**

Для режима `JIRA_MODE=server_6x` проверьте:
- `DEBUG - mcp-jira - Configuring Jira client to use API v2 endpoints`
- `INFO - mcp-jira - Cookie session established successfully` (если используется cookie auth)

### 🐳 Подключение к постоянному контейнеру (без пересоздания)

Для избежания пересоздания контейнера при каждом подключении IDE используйте HTTP transport вместо stdio:

**1. Запустите контейнер в фоне (detached mode):**

```bash
# Для streamable-http transport (рекомендуется)
docker run -d \
  --name mcp-atlassian \
  --restart unless-stopped \
  -p 9000:9000 \
  -e JIRA_MODE=server_6x \
  -e JIRA_URL=https://jira-server.example.com \
  -e JIRA_USERNAME=admin \
  -e JIRA_PASSWORD=password \
  -e JIRA_AUTH=basic \
  -e MCP_VERBOSE=true \
  mcp-atlassian:latest \
  --transport streamable-http --port 9000 --host 0.0.0.0

# Или для SSE transport
docker run -d \
  --name mcp-atlassian \
  --restart unless-stopped \
  -p 9000:9000 \
  -e JIRA_MODE=server_6x \
  -e JIRA_URL=https://jira-server.example.com \
  -e JIRA_USERNAME=admin \
  -e JIRA_PASSWORD=password \
  mcp-atlassian:latest \
  --transport sse --port 9000 --host 0.0.0.0
```

**2. Проверьте, что контейнер запущен:**

```bash
# Проверить статус
docker ps | grep mcp-atlassian

# Просмотр логов
docker logs mcp-atlassian

# Следить за логами в реальном времени
docker logs -f mcp-atlassian
```

**3. Настройте IDE для подключения по HTTP:**

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "url": "http://localhost:9000/mcp"
    }
  }
}
```

Для SSE transport:
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "url": "http://localhost:9000/sse"
    }
  }
}
```

**4. Управление контейнером:**

```bash
# Остановить контейнер
docker stop mcp-atlassian

# Запустить снова
docker start mcp-atlassian

# Перезапустить
docker restart mcp-atlassian

# Просмотр логов
docker logs -f mcp-atlassian

# Последние 100 строк логов
docker logs --tail 100 mcp-atlassian

# Удалить контейнер (остановит и удалит)
docker rm -f mcp-atlassian
```

**5. Автозапуск при перезагрузке:**

Флаг `--restart unless-stopped` автоматически запускает контейнер при перезагрузке системы. Для других вариантов:

```bash
# Всегда перезапускать (даже после остановки)
--restart always

# Только при перезагрузке системы
--restart on-failure
```

> [!IMPORTANT]
> **Отличие от stdio transport:**
> - **stdio** (`--transport stdio`): Контейнер создается и удаляется при каждом подключении IDE
> - **HTTP transport** (`--transport sse` или `streamable-http`): Контейнер работает постоянно, IDE подключается по HTTP

> [!TIP]
> При использовании HTTP транспорта один контейнер может обслуживать несколько подключений IDE одновременно.

## Security

Never share API tokens. Keep `.env` files secure. See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

MIT - See [LICENSE](LICENSE). Not an official Atlassian product.
