# MarcadorReportesPDF (FastAPI) / Proyecto III
### Integrantes: Jenny Sofia Morales López 7690 08 6790 y Cristian Alejandro Melgar Ordoñez 7690 21 8342

Microservicio para **generar reportes en PDF** (equipos, jugadores, historial, roster, scouting) a partir de los datos del backend principal (**API C#**). Se expone vía **FastAPI** y construye PDFs con **ReportLab**.

> Motivos del tipo de implementación: Se obtiene un aislamiento de lógica, generaciones de PDF del backend principal, siendo alimentado por microservicios.

**Dominio registrado** basketmarcador.online

**Llave** ssh -i ~/.ssh/id_ed25519 melgust@91.99.197.226 

**IP Pública** 91.99.197.226

---

## Tabla de contenidos
- [Repositorios](#repositorios)
- [Arquitectura](#arquitectura)
- [Requerimientos](#requerimientos)
- [Estructura del repo](#estructura-del-repo)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Uso del app](#uso-del-app)
- [Endpoints](#endpoints)
- [Integración con Frontend (Angular)](#integración-con-frontend-angular)
- [Integración con Backend (C#)](#integración-con-backend-c)
- [Docker](#docker)
- [Campos esperados del backend](#campos-esperados-del-backend)
- [Manejo de logos en PDF](#manejo-de-logos-en-pdf)
- [Buenas prácticas](#buenas-prácticas)
---
## Repositorios 
Repositorios para Fase III (Proyecto Actual)
- Backend: https://github.com/sofiaMorales3805/MarcadorMicroserviciosBack-Fase3.git 
- Microservicios: https://github.com/sofiaMorales3805/MarcadorReportesPDF-Fase3.git  
- Front: https://github.com/sofiaMorales3805/MarcadorMicroserviciosFront-Fase3 

Repositorios para Fase IV (Proyecto a continuación)

- Gestión de equipos: https://github.com/Alejmm/MicroservicioTeams.git 
- Gestión de jugadores: https://github.com/Alejmm/MicroservicioPlayers.git 
- Gestión y creación de partidos: https://github.com/Alejmm/MicroservicioMatches.git 

---

## Arquitectura

```
[ Angular ]  ──(HTTP)──>  [ FastAPI Reportes ]  ──(HTTP)──>  [ API C# ]
     |                           |                                |
  Usuario                Genera PDF (ReportLab)            Datos/negocio
```

### Funcionamiento principal: 
- La UI (Angular) **abre** URLs `/pdf/...` que atiende cada servicio.
- Este servicio **reenvía** el header `Authorization` hacia la **API C#**.
- Con la data obtenida, construye y devuelve el **PDF** (`application/pdf`).

---

## Requerimientos

- Python 3.11+ (recomendado 3.12)
- Pip / venv
- (Opcional) Docker

Dependencias (archivo `requirements.txt`):

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
requests==2.32.3
reportlab==4.2.5
Pillow==10.4.0
python-dotenv==1.0.1
```

---

## Estructura del repo

```
MarcadorReportesPDF/
├─ app.py                 # FastAPI + endpoints /pdf
├─ requirements.txt       # Dependencias
├─ .env                   # Variables (dev)
├─ README.md              # Este documento
├─ docker/
│  └─ Dockerfile          # (opcional) despliegue
└─ utils/
   └─ pdf_utils.py        # (opcional) helpers de PDF
```

> `utils/pdf_utils.py` es opcional; ayuda a separar estilos y componentes de ReportLab si el proyecto crece.

---
## Despliegue Contenedores

Proceso de empaqueteado en contenedores para la implementación de la aplicación en la VPs, contenedores generados para la entrega del Proyecto Fase III.

![Contenedores](https://github.com/user-attachments/assets/dba299e8-c22d-433b-b531-435ce8744e88)

---

## Instalación y ejecución

```bash
# 1) Crear y activar entorno
python -m venv .venv
# Windows:
. .venv/Scripts/activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Configurar variables
cp .env.example .env   # o crea .env con tus valores

# 4) Ejecutar
uvicorn app:app --reload --port 5055
```

El servicio responderá en `http://localhost:5055`.

---

## Variables de entorno

```
BACK_BASE=http://localhost:5130

EQUIPOS_PATH=/api/equipos
JUGADORES_PATH=/api/jugadores
PARTIDOS_HISTORIAL_PATH=/api/partidos/historial
PARTIDO_ROSTER_PATH=/api/partidos/{id}/roster
SCOUTING_JUGADOR_PATH=/api/estadisticas/jugador/{id}
```

> `PARTIDO_ROSTER_PATH` y `SCOUTING_JUGADOR_PATH` aceptan `{id}`, que el servicio reemplaza por el valor de query.
---
## Uso del app

**Login**

<img width="579" height="514" alt="image" src="https://github.com/user-attachments/assets/12195808-efe9-4aed-8fee-37e5be3b29c8" />

**Creación de usuario**

<img width="458" height="446" alt="image" src="https://github.com/user-attachments/assets/2d8570a8-a9a0-410f-8494-c2fac66d3b6b" />

**Dashboard (Panel administración)**

<img width="1365" height="598" alt="image" src="https://github.com/user-attachments/assets/b792b45a-b862-42a4-a019-aff860bed9d4" />

**Gestión de Equipos**

<img width="1365" height="674" alt="image" src="https://github.com/user-attachments/assets/050fc95d-d8bc-4833-a11a-7356ec78c662" />

**Gestión de Jugadores**

<img width="1365" height="452" alt="image" src="https://github.com/user-attachments/assets/98b0a970-f47d-4707-b1c5-aad44fa2d046" />

**Creación de Torneos**

<img width="1365" height="537" alt="image" src="https://github.com/user-attachments/assets/091232a8-ae52-4538-a5a9-3cdfbc022f8a" />

**Marcador Operador**

<img width="1365" height="678" alt="image" src="https://github.com/user-attachments/assets/fb8f964b-33f7-4074-b2bd-0dcfd799a0e9" />

**Marcador Público**

<img width="1365" height="684" alt="image" src="https://github.com/user-attachments/assets/56f82e95-3a12-41b6-b75d-cb97d9d0de8a" />

**Reportes**
- Jugadores por Equipo
  
<img width="893" height="673" alt="image" src="https://github.com/user-attachments/assets/821811aa-79ba-415c-8a17-f7d4e7b53e39" />

- PDF Descargado Jugadores por Equipo

<img width="852" height="517" alt="image" src="https://github.com/user-attachments/assets/e736d454-30ac-469c-adae-da742e9d2664" />

- Equipos registrados

<img width="446" height="311" alt="image" src="https://github.com/user-attachments/assets/8e92a10a-1436-4447-b87a-7dceb5837499" />

- PDF Descargado Equipos registrados
  
<img width="1003" height="547" alt="image" src="https://github.com/user-attachments/assets/f75b5ee8-73f9-458f-bbce-d9bcb4519733" />

- Estadisticas por jugador

<img width="451" height="322" alt="image" src="https://github.com/user-attachments/assets/ab4b3499-32c8-4c69-b389-f64b3888ebd8" />

- PDF Descargado Estadisticas por jugador

<img width="904" height="373" alt="image" src="https://github.com/user-attachments/assets/416d0ee0-209f-41a9-b520-74bc42f79957" />

- Roster por partidos

<img width="456" height="323" alt="image" src="https://github.com/user-attachments/assets/40b6b632-6567-4ddc-98e5-6356f9c187c8" />

- Historial de partidos

<img width="452" height="264" alt="image" src="https://github.com/user-attachments/assets/b4f412ec-6b43-4176-940f-fb0d682c2e3c" />

- PDF Descargado Historial de partidos

<img width="791" height="519" alt="image" src="https://github.com/user-attachments/assets/262dc186-379b-48c5-b79e-68714f399f34" />

---

## Endpoints

Todos devuelven **PDF** y aceptan el header `Authorization` para reenviarlo a la API C#.

### `GET /`
Salud del servicio.
- **200** `{ "message": "Marcador Reportes API", "version": "1.0.0" }`

### `GET /pdf/equipos`
Lista de equipos en tabla con: **Id**, **Logo**, **Equipo**, **Ciudad**, **Puntos**, **Faltas**.  
Query opcionales: `search`, `ciudad`.

### `GET /pdf/jugadores-por-equipo?equipoId={id}`
Tabla con: **#**, **Jugador**, **Posición**, **Núm.**, **Edad**, **Estatura (cm)**, **Nacionalidad**.

### `GET /pdf/historial-partidos?temporadaId={id?}`
Tabla con: **#**, **Local**, **Visitante**, **Fecha/Hora**, **Marcador**.  
Si no se envía `temporadaId`, retorna el historial general (paginado internamente a 500 filas por PDF).

### `GET /pdf/roster?partidoId={id}`
Tabla con: **#**, **EquipoId**, **Jugador**, **Posición**.

### `GET /pdf/scouting?jugadorId={id}`
Ficha individual tipo scouting con métricas: **PPG, RPG, APG, SPG, BPG, FG%, 3P%, FT%, MIN, TOV, PF**.  
El título incluye **nombre, equipo, edad y estatura** si están disponibles.

**Ejemplos cURL**

```bash
curl -H "Authorization: Bearer <token>"      -o equipos.pdf      http://localhost:5055/pdf/equipos

curl -H "Authorization: Bearer <token>"      -o jugadores_equipo.pdf      "http://localhost:5055/pdf/jugadores-por-equipo?equipoId=5"
```

---

## Integración con Frontend (Angular)

### Proxy de desarrollo

`proxy.conf.json`
```json
{
  "/api": { "target": "http://localhost:5130", "secure": false, "changeOrigin": true },
  "/pdf": { "target": "http://localhost:5055", "secure": false, "changeOrigin": true }
}
```

`package.json`
```json
{
  "scripts": {
    "start": "ng serve --proxy-config proxy.conf.json"
  }
}
```

### Abrir PDFs desde la UI

```ts
private open(url: string) { window.open(url, '_blank'); }

openEquipos()                     { this.open('/pdf/equipos'); }
openJugadoresPorEquipo(id: number){ this.open(`/pdf/jugadores-por-equipo?equipoId=${id}`); }
openHistorial(t?: number|null)    { this.open(`/pdf/historial-partidos${t ? `?temporadaId=${t}` : ''}`); }
openRoster(id: number)            { this.open(`/pdf/roster?partidoId=${id}`); }
openScouting(id: number)          { this.open(`/pdf/scouting?jugadorId=${id}`); }
```

---

## Integración con Backend (C#)

Este servicio consulta la API C# con `requests.get(...)`/`requests.post(...)` y **reenvía** el header:

```py
def _hdr(authorization: str | None):
    return {"Authorization": authorization} if authorization else {}
```

Asegúrate de que la API C#:
- Acepte el token JWT del usuario.
- Devuelva **los campos** que el PDF requiere (ver sección siguiente).
- Permita filtros por query (`equipoId`, `temporadaId`, etc.).

---

## Docker

`docker/Dockerfile`
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5055
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5055"]
```

Construir y ejecutar:

```bash
docker build -t marcador-reportes .
docker run --env-file .env -p 5055:5055 marcador-reportes
```

---

## Campos esperados del backend

El servicio es tolerante con nombres `camelCase` / `PascalCase` / `snake_case`.  
Aun así, conviene unificar:

### Equipos
- `id`, `nombre`, `ciudad`, `puntos`, `faltas`, `logoUrl` (o `logo`)

### Jugadores
- `nombre`, `posicion`, `numero`, `edad`, `estatura`, `nacionalidad`, `equipoId`

### Historial de partidos
- `equipoLocalNombre` / `equipoLocalId`
- `equipoVisitanteNombre` / `equipoVisitanteId`
- `fechaHora`
- `marcadorLocal`, `marcadorVisitante`

### Roster por partido
- `equipoId`, `jugadorNombre` (o `jugadorId`), `posicion`

### Scouting jugador
- `nombre`, `equipoNombre`, `edad`, `estatura`
- Métricas: `ppg`, `rpg`, `apg`, `spg`, `bpg`, `fgp`, `tpp`, `ftp`, `min`, `tov`, `pf`

> Si cambias nombres, ajusta los `.get()` en `app.py` o mapea desde la API C#.

---

## Manejo de logos en PDF

- Si el equipo tiene `logoUrl` (o `logo`), el servicio intenta **descargar** la imagen y la **redimensiona** con **Pillow** para insertarla en la tabla.
- Si falla la descarga o el campo está vacío, se imprime un guion `—` en su lugar.
- Tamaño aproximado de celda: `1.0 inch` (configurable en `_img_from_url`).

---

## Buenas prácticas

- Limitar el número de filas por PDF (paginación) si la data puede ser muy grande.
- Centralizar estilos y componentes de ReportLab en `utils/pdf_utils.py`.
- Añadir **tests** que simulen respuestas de la API C# (con `responses` o `pytest-httpserver`).
- Versionar el microservicio (tag de imagen Docker y variable `version` en `app:app`).

---
