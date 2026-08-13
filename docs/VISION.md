# Vision — GhostTown

**EN**: **Local** app: backup Gmail to PC → read offline → (optional) clean commercial spam with OpenAI.  
**ES**: App **local**: respaldar Gmail en la PC → leer offline → (opcional) limpiar basura comercial con OpenAI.

```
Gmail IMAP → data/ → ghosttown/ → http://127.0.0.1:8765
```

## Phases / Fases

| # | What / Qué | Notes / Notas |
|---|------------|---------------|
| 1 | IMAP Backup + Gmail-like UI / Respaldo IMAP + UI tipo Gmail | Mandatory; no OpenAI / Obligatoria; sin OpenAI |
| 2 | AI proposes commercial cleanup / IA propone borrar comercial | Optional; **user confirms** / Opcional; **usuario confirma** |

## Golden Rule / Regla de oro

**EN**: No deletion without prior backup. When in doubt → **keep**. Deleting = moving to Gmail Trash (reversible).  
**ES**: Sin respaldo previo, no se borra. Ante la duda → **conservar**. Borrar = mover a Papelera Gmail (reversible).

## Keep / Conservar

**EN**: Important documents, personal conversations, contacts, legal records, bank statements, health information, important attachments.  
**ES**: Documentos importantes, conversaciones personales, contactos, legales, estado de cuenta, información de salud, adjuntos importantes.

## Trash Candidates (only after confirm) / Candidato a borrar (solo tras confirmar)

**EN**: Newsletters, promos, ads, automated marketing, repetitive commercial no-reply emails.  
**ES**: Newsletters, promos, ads, marketing automático, no-reply comercial repetido.

## What it is NOT / Qué NO es

**EN**: It is not a full email client. Just local read-only backup + sync + confirmed cleanup.  
**ES**: No es un cliente de correo completo. Solo lectura local + sync + limpieza confirmada.
