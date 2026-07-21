# Vision

## Idea (ES)
Backup local de Gmail → leer offline en UI tipo Gmail → liberar espacio en Gmail/Drive. Luego (opcional) IA ayuda a limpiar mugrero; si borra de más, ya está en GhostTown.

## Idea (EN)
Local Gmail backup → read offline in a Gmail-like UI → free mailbox/Drive space. Optional AI helps delete commercial spam; GhostTown is the safety net.

## Flujo
```
Gmail IMAP → data/ (cache) → ghosttown/ (HTML + messages.json) → http://127.0.0.1:8765
```

## Qué NO es
No es un cliente de correo completo. Solo lectura local + sync + limpieza confirmada.
