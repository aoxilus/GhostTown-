# UI — stats, folders, pagination

## Sidebar / Barra lateral
**EN**:
- **All / Todos** → emails from `[Gmail]/All Mail` (unique ~complete corpus)
- **Inbox / Sent / …** → Gmail folders + custom labels (remote count)
- Counters use IMAP `folder_totals` (`MESSAGES`), not just what's downloaded.
**ES**:
- **Todos** → correos de `[Gmail]/All Mail` (corpus único ~completo)
- **Recibidos / Enviados / …** → carpetas Gmail + labels custom (conteo remoto)
- Contadores usan `folder_totals` de IMAP (`MESSAGES`), no solo lo ya bajado.

## Stats (bottom of sidebar / abajo en sidebar)
**EN**:
- **% Ring** = downloaded / remote total (All Mail)
- Numbers: `downloaded of total`
- **Last update** = `data/state.json` → `last_sync`
- Badge **✓ FULL BACKUP · X GB** (green if 100%, amber if partial)
**ES**:
- Anillo **%** = descargados / total remoto (All Mail)
- Números: `descargados de total`
- **Última actualización** = `data/state.json` → `last_sync`
- Badge **✓ FULL BACKUP · X GB** (verde si 100%, ámbar si parcial)

## Backup log / Historial de backup
**EN**:
- `data/backup_log.json` — history (each `build` adds an entry, max 100)
- Fields: `date`, `type` (full/partial), `messages`, `of`, `percent`, `disk`
**ES**:
- `data/backup_log.json` — historial (cada `build` agrega entrada, máx 100)
- Campos: `date`, `type` (full/partial), `messages`, `of`, `percent`, `disk`

## Pagination / Paginación
**EN**:
- **250 emails per page**
- Lightweight index: `ghosttown/messages.json` (no 26k `<li>` in HTML)
- Prev/next at the top and bottom
**ES**:
- **250 correos por página**
- Índice liviano: `ghosttown/messages.json` (no 26k `<li>` en HTML)
- Prev/next arriba y abajo

## Folder Sync / Sync de carpetas
**EN**: 
By default downloads: All Mail, INBOX, Sent + custom labels.
**Never copies Trash / Spam / Drafts** (nor do they appear in the sidebar); explicit sync with `--folder` if needed.
**ES**: 
Por defecto baja: All Mail, INBOX, Sent + labels custom.
**Nunca copia Trash / Spam / Drafts** (ni aparecen en el sidebar); sync explícito con `--folder` si se quisieran.

## Fast Rebuild / Rebuild rápido
**EN**: `build` does not rewrite existing HTML threads (only index + new pages).
**ES**: `build` no reescribe threads HTML que ya existen (solo índice + pages nuevas).
