## 1. Começando do zero

No Linux:

```bash
mkdir mousemover
cd mousemover

git init -b main
```

Primeiro crie **somente** o `.gitignore`:

```bash
code .gitignore
```

Conteúdo:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
env/

# Build / packaging
build/
dist/
*.spec
*.egg-info/

# IDE
.vscode/
.idea/

# Runtime
*.log
*.lock
config.ini
external_plugins/

# OS
.DS_Store
Thumbs.db
```

Agora seu **primeiro commit exclusivamente do `.gitignore`**:

```bash
git add .gitignore
git commit -m "chore: add initial gitignore"
```

Se o repositório já foi criado no GitHub:

```bash
git remote add origin <URL_DO_SEU_REPOSITORIO>
git push -u origin main
```

Por exemplo:

```bash
git remote add origin git@github.com:SEU_USUARIO/mousemover.git
git push -u origin main
```

---

# 2. Agora coloque o projeto

A estrutura do projeto ficou assim:

```text
mousemover/
│
├── .gitignore
├── README.md
├── pyproject.toml
├── launcher.py
│
├── config.json
├── config.ini.example
│
├── scripts/
│   ├── build_linux.sh
│   └── build_windows.bat
│
└── src/
    └── mousemover/
        │
        ├── __init__.py
        ├── cli.py
        ├── gui.py
        ├── models.py
        │
        ├── core/
        │   ├── __init__.py
        │   ├── config.py
        │   ├── engine.py
        │   ├── input_hooks.py
        │   ├── logger.py
        │   ├── monitors.py
        │   ├── paths.py
        │   ├── plugin_loader.py
        │   └── single_instance.py
        │
        └── plugins/
            ├── __init__.py
            ├── basic.py
            ├── circle.py
            ├── erosion.py
            ├── fractal_walk.py
            ├── nudge_diagonal.py
            ├── nudge_human_30s.py
            ├── nudge_noise.py
            ├── nudge_smart.py
            ├── one_pixel_nudge.py
            ├── random_walk.py
            ├── spiral.py
            ├── square.py
            └── zigzag.py
```

Usei **`src` layout**, que separa o código importável dos arquivos da raiz e reduz vários problemas de import durante desenvolvimento/empacotamento. É justamente uma das vantagens recomendadas pelo Python Packaging Guide. ([Guia do Usuário de Empacotamento Python][1])

Depois:

```bash
git status
git add .
git commit -m "feat: add initial MouseMover application"
git push
```

---

# 3. Arquitetura

A parte importante ficou assim:

```text
                   launcher.py
                       │
              ┌────────┴────────┐
              │                 │
             GUI               CLI
          gui.py              cli.py
              │                 │
              └────────┬────────┘
                       │
                   Engine
               core/engine.py
                       │
             ┌─────────┼─────────┐
             │         │         │
          Monitor    Hooks     Plugins
```

Ou seja:

**não existe um motor para CLI e outro para GUI.**

Os dois chamam:

```python
Engine(...)
```

Isso era importante para não termos:

```text
bug corrigido na GUI
+
bug ainda existente na CLI
```

---

# 4. Criando o ambiente Linux

No Ubuntu:

```bash
sudo apt update
sudo apt install -y python3-venv python3-tk
```

Crie o venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Atualize pip:

```bash
python -m pip install --upgrade pip
```

Instale o projeto em modo desenvolvimento:

```bash
pip install -e ".[dev]"
```

O Tkinter é a interface padrão do Python para Tcl/Tk e está disponível nas principais plataformas. ([Python documentation][2])

Pode testar:

```bash
python -m tkinter
```

Se abrir uma janelinha, está funcionando.

---

# 5. Rodando a GUI

Com o venv ativo:

```bash
mousemover-gui
```

ou:

```bash
python -m mousemover.gui
```

A GUI já possui:

* seleção de monitor;
* resolução/posição/orientação;
* seleção de plugin;
* reload dos plugins;
* intervalo;
* jitter mínimo;
* jitter máximo;
* watchdog;
* mouse hook;
* once;
* headless;
* force;
* execução em segundo plano;
* teste do monitor;
* iniciar;
* parar;
* log em tempo real.

E:

```text
Ctrl + Shift + F9
    Pausa

Ctrl + Shift + F10
    Continua

Ctrl + Shift + F12
    Para o loop

ESC
    Mata o aplicativo inteiro
```

Para os atalhos globais foi usado o mecanismo `GlobalHotKeys` do `pynput`, feito justamente para registrar hotkeys independentes do foco da aplicação. ([Pynput][3])

---

# 6. CLI

Com o projeto instalado:

```bash
mousemover --help
```

Listar monitores:

```bash
mousemover --list-monitors
```

Exemplo:

```text
0 | eDP-1 | 1920x1080 | X=0 Y=0 | Landscape | Principal
1 | HDMI-1 | 1920x1080 | X=1920 Y=0 | Landscape
```

Listar plugins:

```bash
mousemover --list-plugins
```

Algo como:

```text
basic
circle
erosion
fractal_walk
nudge_diagonal_1px
nudge_humano_30s
nudge_inteligente
nudge_noise_1px
one_pixel_nudge
random_walk
spiral
square
zigzag
```

---

# 7. Seu `nudge_inteligente`

Por exemplo:

```bash
mousemover \
    --plugin nudge_inteligente \
    --monitor 0 \
    --interval 30 \
    --daemon
```

Ele move apenas:

```text
1px ↑
ou
1px ↓
ou
1px ←
ou
1px →
```

e antes verifica se a coordenada pertence a algum monitor existente.

---

# 8. Plugin humano de 30 segundos

Esse recebeu uma pequena melhoria importante na versão final.

Execute:

```bash
mousemover \
    --plugin nudge_humano_30s \
    --monitor 0 \
    --interval 1 \
    --daemon
```

Funcionamento:

```text
Usuário mexeu
      ↓
   espera
      ↓
30 segundos parado
      ↓
move 1 px
      ↓
   espera
      ↓
30 segundos
      ↓
move 1 px
```

O movimento gerado pelo próprio MouseMover **não é interpretado pelo hook como movimento humano**.

Isso evita o programa se autossabotar.

---

# 9. Sensor global de movimento

Por padrão:

```text
False
```

Como você pediu.

Para habilitar via CLI:

```bash
mousemover \
    --plugin nudge_inteligente \
    --mouse-hook \
    --interval 30 \
    --daemon
```

Se você mexer fisicamente no mouse:

```text
movimento humano
       ↓
mouse hook
       ↓
interrompe loop
       ↓
log
```

Sem ele:

```bash
--no-mouse-hook
```

---

# 10. JSON + INI

Temos os dois, mas com responsabilidades diferentes.

### `config.json`

Configuração:

```json
{
    "movement_plugin": "nudge_inteligente",
    "interval_seconds": 30,
    "jitter_min": 1,
    "jitter_max": 10,
    "watchdog_timeout": 3,
    "mouse_hook": false,
    "monitor_index": 0,
    "log_level": "info"
}
```

### `config.ini`

Estado persistente:

```ini
[state]
monitor_index = 0
plugin = nudge_inteligente
mouse_hook = false
```

Prioridade:

```text
DEFAULT Python
      ↓
config.json
      ↓
config.ini
      ↓
CLI
```

Então:

```bash
mousemover --interval 5
```

ganha do:

```json
"interval_seconds": 30
```

E:

```bash
--force
```

ignora completamente JSON e INI.

---

# 11. Plugins externos

Essa ficou uma parte bem interessante.

O programa cria:

```text
plugins/
```

**ao lado do executável.**

Você pode jogar:

```text
plugins/meu_plugin.py
```

sem recompilar o programa.

Exemplo:

```python
class MovementPlugin:
    name = "teste_1px"

    def get_next_points(self, ctx):
        return [
            (
                ctx.current_x + 1,
                ctx.current_y
            )
        ]
```

Na GUI:

```text
Reload plugins
```

Pronto.

Se editar:

```text
meu_plugin.py
```

e clicar novamente:

```text
Reload plugins
```

a nova implementação entra sem reiniciar o aplicativo.

---

# 12. Um único aplicativo

Aqui alterei um ponto em relação à proposta anterior.

Agora existe:

```text
launcher.py
```

Ele decide:

```text
MouseMover
    │
    ├── nenhum argumento
    │       ↓
    │      GUI
    │
    └── recebeu argumentos
            ↓
           CLI
```

Portanto no Windows você pode distribuir **um único arquivo**:

```text
MouseMover.exe
```

Dê duplo clique:

```text
MouseMover.exe
```

→ abre GUI.

Abra CMD:

```bat
MouseMover.exe --help
```

→ CLI.

Por exemplo:

```bat
MouseMover.exe ^
    --plugin nudge_inteligente ^
    --monitor 1 ^
    --interval 30 ^
    --daemon
```

→ execução CLI.

No Windows, o launcher tenta ocultar o console quando aberto **sem argumentos**, então o usuário vê somente a GUI.

---

# 13. Build Linux

Já criei:

```text
scripts/build_linux.sh
```

Execute:

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

Ele usa PyInstaller com `--onefile`.

O PyInstaller coleta o interpretador Python, módulos e dependências e pode empacotá-los em um único executável. ([PyInstaller][4])

Resultado:

```text
dist/
└── MouseMover
```

Agora:

```bash
./dist/MouseMover
```

GUI.

E:

```bash
./dist/MouseMover --list-plugins
```

CLI.

---

# 14. Build Windows `.exe`

Aqui está um detalhe importante:

**eu recomendo fazer o build Windows no próprio Windows**.

O bootloader do PyInstaller é específico da plataforma em execução, então esse é o fluxo mais previsível para produzir o `.exe`. ([PyInstaller][4])

No Windows:

```bat
git clone <SEU_REPOSITORIO>
cd mousemover
```

Crie venv:

```bat
python -m venv .venv
```

Ative:

```bat
.venv\Scripts\activate
```

Atualize:

```bat
python -m pip install --upgrade pip
```

E:

```bat
scripts\build_windows.bat
```

Resultado:

```text
dist\
└── MouseMover.exe
```

---

# 15. O usuário final

Agora chegamos exatamente no objetivo.

Você publica:

```text
MouseMover.exe
```

O usuário baixa:

```text
MouseMover.exe
```

Dá duplo clique:

```text
┌───────────────────────────┐
│        MouseMover         │
│                           │
│ Monitor: [.............]  │
│ Plugin:  [.............]  │
│                           │
│ Intervalo: [30]           │
│ Jitter min: [1]           │
│ Jitter max: [10]          │
│ Watchdog: [3]             │
│                           │
│ ☐ Sensor mouse            │
│ ☐ Once                    │
│ ☐ Segundo plano           │
│                           │
│ [ Iniciar ] [ Parar ]     │
│                           │
│ Logs...                   │
└───────────────────────────┘
```

Ele **não precisa instalar Python, pip, pynput, screeninfo ou pyautogui**. Esse é exatamente o modelo standalone do PyInstaller. ([PyInstaller][4])

O executável usa `sys.executable` quando congelado para descobrir corretamente o diretório do próprio `.exe`, algo documentado pelo próprio PyInstaller. ([PyInstaller][5])

---

## 16. README

O ZIP já contém um **`README.md` completo**, com:

* instalação para desenvolvimento;
* criação do venv;
* interface gráfica;
* CLI;
* todas as principais flags;
* exemplos;
* JSON;
* INI;
* plugins;
* reload;
* `nudge_inteligente`;
* `nudge_humano_30s`;
* logs;
* hotkeys;
* build Linux;
* build Windows;
* distribuição final.

Então o fluxo agora pode ser:

```bash
git add .
git commit -m "feat: add CLI GUI engine and movement plugins"
git push
```

Depois disso, eu seguiria com uma etapa separada de **teste no seu Linux antes de sequer pensar no `.exe`**: instalar o projeto no `.venv`, rodar `--list-monitors`, `--list-plugins`, testar primeiro `nudge_inteligente`, testar as hotkeys globais e só depois abrir a GUI. Isso vai isolar qualquer problema de X11/Wayland antes de misturarmos PyInstaller na história. ([Python documentation][2])

[1]: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/?utm_source=chatgpt.com "src layout vs flat layout"
[2]: https://docs.python.org/3/library/tkinter.html?utm_source=chatgpt.com "tkinter — Python interface to Tcl/Tk"
[3]: https://pynput.readthedocs.io/en/latest/keyboard.html?utm_source=chatgpt.com "Handling the keyboard — pynput 1.7.6 documentation"
[4]: https://pyinstaller.org/en/stable/operating-mode.html?utm_source=chatgpt.com "What PyInstaller Does and How It Does It"
[5]: https://pyinstaller.org/en/stable/runtime-information.html?utm_source=chatgpt.com "Run-time Information — PyInstaller 6.22.0 documentation"
