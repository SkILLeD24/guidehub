# GuideHub

Platforma web pentru descoperire de jocuri, publicare de articole si moderare pe roluri.

## Ce include proiectul

- autentificare cu sesiune (`guest`, `user`, `admin`)
- catalog de jocuri cu metadate extinse (studio, an, platforme, surse)
- submit de articole + moderare (`pending` -> `approved` / `rejected`)
- dashboard admin + workspace dedicat pentru management articole
- date seed pentru demo: 26 jocuri, 100 articole approved, articole pending

## Cerinte

- Python 3.10+ (recomandat 3.11/3.12)
- pip
- Windows / Linux / macOS

## Instalare si rulare rapida

1. Deschide terminalul in folderul proiectului.
2. (Optional, recomandat) creeaza un mediu virtual.
3. Instaleaza dependintele.
4. Genereaza baza de date seed.
5. Porneste serverul Flask.

### Comenzi (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
python app.py
```

### Comenzi (Linux/macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

Aplicatia va fi disponibila implicit la:

- `http://127.0.0.1:5000`

## Conturi demo

Se creeaza automat la `python init_db.py`:

- admin
  - email: `giku@example.com`
  - parola: `1234`
- user
  - `alex@example.com` / `1234`
  - `bianca@example.com` / `1234`
  - `pufu@example.com` / `1234`

## Structura fisierelor principale

- `app.py` - backend Flask + API + acces pe roluri
- `init_db.py` - creare schema + seed data
- `script.js` - logica frontend (home/game/admin/article management)
- `style.css` - stiluri globale
- `index.html` - homepage
- `game.html` - pagina detaliu joc
- `submit.html` - submit articole
- `admin.html` - dashboard admin (publicare, moderare, add game)
- `article-management.html` - management articole per joc (popup modal)

## Flux de test recomandat (demo)

1. Intra ca `guest` pe homepage (doar browse).
2. Login ca `user` si trimite un articol (status `pending`).
3. Login ca `admin` si aproba/rejecteaza articolul.
4. Verifica aparitia in listele publice (`Latest approved articles`, pagina joc).
5. Testeaza `Article Management` pe jocuri, cu popup + edit/delete.

## Configurare (optional)

Pentru sesiuni mai sigure in medii non-demo:

- seteaza variabila de mediu `GUIDEHUB_SECRET_KEY`

Exemplu (PowerShell):

```powershell
$env:GUIDEHUB_SECRET_KEY="schimba-cu-o-cheie-lunga-si-random"
python app.py
```

## Troubleshooting

- Daca nu vezi schimbarile UI: `Ctrl + F5` (hard refresh).
- Daca apar erori pe DB dupa schimbari de seed/schema: ruleaza din nou `python init_db.py`.
- Daca portul 5000 e ocupat: opreste procesul existent sau porneste pe alt port.

## Git

Fisierul `.gitignore` exclude:

- `__pycache__/`
- `*.py[cod]`
- `guidehub.db`

Astfel, fiecare coleg isi poate regenera local baza de date din seed.
