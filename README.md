# GmailGhostTown

Convierte tu Gmail en un pueblo fantasma: baja todo tu correo a tu PC como un sitio HTML navegable, y despues un asistente de IA (`gpt-4.1-mini`) te ayuda a limpiar el mugrero (newsletters, anuncios, ventas) mandandolo a la papelera. Como ya tienes la copia local, puedes vaciar Gmail sin miedo.

---

## Inicio rapido (doble clic)

1. Instala **Python 3.11 o mas** desde [python.org](https://www.python.org/downloads/) (marca "Add Python to PATH").
2. Doble clic en **`GhostTown.bat`**.
   - La primera vez instala todo solo (1-2 min).
   - Se abre una ventana que pide tus datos.
3. Llena la ventana, clic en **Verificar y abrir GhostTown**.

Eso es todo. Si el login es correcto, baja tu correo y abre `http://127.0.0.1:8765`.

---

## Paso a paso: crear el App Password de Google

Google no deja usar tu contrasena normal para esto. Necesitas un **App Password** (16 letras). Solo se hace una vez.

1. **Usa tu cuenta personal de Gmail** (no una escolar/empresa; esas suelen tenerlo bloqueado).
2. **Activa la Verificacion en 2 pasos:**
   - Entra a [myaccount.google.com/security](https://myaccount.google.com/security)
   - Busca **Verificacion en 2 pasos** y actavala (te pedira tu telefono).
   - Sin este paso, Google esconde los App Passwords.
3. **Activa IMAP en Gmail:**
   - Abre Gmail -> engranaje **Configuracion** -> **Ver toda la configuracion**
   - Pestana **Reenvio y correo POP/IMAP** -> **Habilitar IMAP** -> Guardar.
4. **Crea el App Password:**
   - Entra a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - En **Nombre de la app** escribe: `GhostTown`
   - Clic en **Crear**.
5. Google muestra **16 letras** (ej. `abcd efgh ijkl mnop`). Copialas.
   - En la ventana de GhostTown pegalas en **App Password** (los espacios no importan).

> Si en el paso 4 dice "The setting you are looking for is not available":
> - Te falta activar la Verificacion en 2 pasos (paso 2), **o**
> - Estas en una cuenta escolar/empresa que lo bloquea. Cambia a tu Gmail personal.

---

## OpenAI API Key (opcional)

Solo se necesita para el chat que limpia el correo con IA. Para **solo respaldar** (GhostTown) puedes dejarla vacia.

- Consiguela en [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
- El modelo por defecto es `gpt-4.1-mini` (barato).

---

## Como se usa GhostTown

- **Buscar:** barra arriba filtra tus correos.
- **Abrir:** clic en un correo para ver la conversacion y adjuntos.
- **Guardian (chat a la derecha):** escribe cosas como
  - "borra todos los newsletters y anuncios"
  - "que correos comerciales hay de 2023"
- La IA propone una lista para borrar. **Nada se borra sin que confirmes.** Revisas y clic en **Confirmar Trash** -> se mueve a la papelera de Gmail.

---

## Para usuarios avanzados (linea de comandos)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # edita con tus datos
python -m src.cli verify         # prueba el login IMAP
python -m src.cli sync --limit 50  # baja 50 para probar
python -m src.cli serve          # abre la UI + chat
```

| Comando | Que hace |
|---------|----------|
| `python -m src.cli verify` | Prueba el login IMAP y sale |
| `python -m src.cli sync` | Baja el correo (usa `--limit N` para probar) |
| `python -m src.cli build` | Regenera el HTML |
| `python -m src.cli serve` | Abre GhostTown + chat IA |

Quita `--limit` para bajar **todo** el correo.

---

## Privacidad

Todo corre en tu PC. Tu correo se guarda en `data/` y `ghosttown/` (ignorados por git). Tus claves viven solo en `.env` local. Lo unico que sale a internet es: IMAP hacia Google y, si usas el chat, los asuntos/remitentes hacia OpenAI para clasificar.
