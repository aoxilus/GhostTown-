# UI — stats, folders, pagination

## Sidebar
- **Todos** → correos de `[Gmail]/All Mail` (corpus único ~completo)
- **Recibidos / Enviados / …** → carpetas Gmail + labels custom (conteo remoto)
- Contadores usan `folder_totals` de IMAP (`MESSAGES`), no solo lo ya bajado

## Stats (abajo en sidebar)
- Anillo **%** = descargados / total remoto (All Mail)
- Números: `descargados de total`
- **Última actualización** = `data/state.json` → `last_sync`

## Paginación
- **250 correos por página**
- Índice liviano: `ghosttown/messages.json` (no 26k `<li>` en HTML)
- Prev/next arriba y abajo

## Sync de carpetas
Por defecto baja: All Mail, INBOX, Sent + labels custom.
**Nunca copia Trash / Spam / Drafts** (ni aparecen en el sidebar); sync explícito con `--folder` si se quisieran.

## Rebuild rápido
`build` no reescribe threads HTML que ya existen (solo índice + pages nuevas).
