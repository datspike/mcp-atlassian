# Локальный деплой mcp-atlassian

## Репозиторий

Форк: `datspike/mcp-atlassian` (origin)
Оригинал: `sooperset/mcp-atlassian` (upstream)

Локальные коммиты поверх upstream:
- Jira 6x mode via basic auth
- Jira Comments: MCP tools get_comments, get_comment + comment_limit fix

## Контейнеры

### mcp-atlassian (SSE, порт 9000)

```bash
docker run -d --name mcp-atlassian \
  -p 9000:9000 \
  -e JIRA_AUTH=basic \
  -e JIRA_MODE=server_6x \
  -e JIRA_URL=https://jira.teleformis.ru \
  -e JIRA_USERNAME=a.elesin \
  -e JIRA_PASSWORD=<password> \
  -e ENABLED_TOOLS=jira_search,jira_get_issue,jira_get_transitions,jira_search_fields,jira_update_issue,jira_add_comment,jira_add_worklog,jira_transition_issue,jira_get_comments,jira_get_comment \
  mcp-atlassian:latest \
  --transport sse --port 9000 -vv
```

### mcp-atlassian-codex (streamable-http, порт 9001)

```bash
docker run -d --name mcp-atlassian-codex \
  -p 9001:9000 \
  -e JIRA_AUTH=basic \
  -e JIRA_MODE=server_6x \
  -e JIRA_URL=https://jira.teleformis.ru \
  -e JIRA_USERNAME=a.elesin \
  -e JIRA_PASSWORD=<password> \
  -e ENABLED_TOOLS=jira_search,jira_get_issue,jira_get_transitions,jira_search_fields,jira_update_issue,jira_add_comment,jira_add_worklog,jira_transition_issue,jira_get_comments,jira_get_comment \
  mcp-atlassian:latest \
  --transport streamable-http --port 9000 --path /mcp -vv
```

## Обновление

```bash
# 1. Получить обновления upstream
git fetch upstream

# 2. Rebase локальных коммитов
git rebase upstream/main

# 3. Разрешить конфликты (ожидаемо в servers/jira.py, jira/comments.py, jira/config.py)
# git add <files> && git rebase --continue

# 4. Push в форк
git push origin main --force

# 5. Пересобрать образ
docker build -t mcp-atlassian:latest .

# 6. Пересоздать контейнеры
docker stop mcp-atlassian mcp-atlassian-codex
docker rm mcp-atlassian mcp-atlassian-codex
# Запустить заново (команды выше)
```

## Проверка

```bash
docker ps | grep mcp
docker logs mcp-atlassian --tail 10
docker logs mcp-atlassian-codex --tail 10
```
