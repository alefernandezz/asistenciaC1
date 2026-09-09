# Moodle Attendance Watcher

Te avisa por mail cuando la profesora habilita la actividad **"Asistencia TT"**
en Moodle, para que entres vos mismo a marcarla. **No marca la asistencia
automáticamente por vos** — eso queda siempre en tus manos.

## Cómo funciona

1. Corre automáticamente los **miércoles y viernes de 15:00 a 19:00hs**
   (hora Argentina), revisando cada 15 minutos.
2. Inicia sesión en Moodle con tu usuario y contraseña.
3. Busca si el texto "Asistencia TT" aparece en la página del curso
   (cuando está oculta, no aparece; cuando la profesora la habilita, sí).
4. Si aparece por primera vez, te manda un mail. No te vuelve a mandar
   mails repetidos mientras siga habilitada (usa un archivo de estado).

## Configuración (una sola vez)

### 1. Crear un repositorio en GitHub

Subí esta carpeta a un repositorio **privado** en tu cuenta de GitHub
(privado es importante, aunque las credenciales van en Secrets y no en
el código).

### 2. Generar una contraseña de aplicación de Gmail

1. Andá a https://myaccount.google.com/apppasswords
2. Generá una contraseña de aplicación (necesitás tener la verificación
   en dos pasos activada en tu cuenta de Google).
3. Copiá la contraseña de 16 caracteres que te da.

### 3. Cargar los Secrets en GitHub

En tu repositorio: **Settings → Secrets and variables → Actions → New
repository secret**. Cargá estos 5:

| Nombre | Valor |
|---|---|
| `MOODLE_USER` | Tu usuario de Moodle |
| `MOODLE_PASS` | Tu contraseña de Moodle |
| `GMAIL_USER` | Tu dirección de Gmail |
| `GMAIL_APP_PASSWORD` | La contraseña de aplicación de 16 caracteres |
| `NOTIFY_EMAIL` | A dónde querés que llegue el aviso (puede ser el mismo Gmail) |

### 4. Probarlo manualmente

En GitHub: **Actions → Check Moodle TT Attendance → Run workflow**.
Así lo probás sin esperar al miércoles/viernes.

## Si algo no funciona

- Si Moodle cambia su formulario de login o el nombre de la actividad,
  el script te va a mandar un mail de error en vez de fallar en
  silencio.
- Si el texto de la actividad no es exactamente "Asistencia TT", editá
  la variable `TARGET_PATTERN` en `check_attendance.py`.
- Revisá los logs en la pestaña **Actions** de GitHub para ver el
  detalle de cada corrida.

## Importante

- Tus credenciales de Moodle quedan guardadas como Secrets de GitHub
  (encriptadas, no visibles en el código ni en los logs).
- Revisá el reglamento de tu universidad sobre uso de scripts contra
  sus plataformas — este script solo *lee* información pública de tu
  cuenta, nunca envía ni modifica datos de asistencia.
