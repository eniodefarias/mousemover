# MouseMover

Utilitário Python para movimentação controlada do mouse com:

- interface gráfica Tkinter;
- modo CLI;
- plugins de movimento;
- múltiplos monitores;
- hotkeys globais;
- sensor opcional de movimento do usuário;
- watchdog;
- logs;
- proteção contra múltiplas instâncias;
- configurações JSON + INI.

## Hotkeys globais

| Atalho | Ação |
|---|---|
| `Ctrl+Shift+F9` | Pausar o loop |
| `Ctrl+Shift+F10` | Continuar |
| `Ctrl+Shift+F12` | Parar o loop |
| `ESC` | Encerrar completamente o aplicativo |

O `ESC` é a tecla de emergência e funciona mesmo quando outra janela está em foco, desde que o backend de captura global do sistema operacional permita.

## Estrutura

```text
mousemover/
├── .gitignore
├── README.md
├── pyproject.toml
├── launcher.py
├── config.json
├── config.ini.example
├── scripts/
│   ├── build_linux.sh
│   └── build_windows.bat
└── src/
    └── mousemover/
        ├── __init__.py
        ├── cli.py
        ├── gui.py
        ├── models.py
        ├── core/
        │   ├── config.py
        │   ├── engine.py
        │   ├── input_hooks.py
        │   ├── logger.py
        │   ├── monitors.py
        │   ├── paths.py
        │   ├── plugin_loader.py
        │   └── single_instance.py
        └── plugins/
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

## Desenvolvimento no Linux

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y python3-venv python3-tk
```

Crie o ambiente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Teste o Tkinter:

```bash
python -m tkinter
```

### Atenção a Wayland

Captura global de teclado/mouse pode depender do backend e das permissões do ambiente gráfico. Se o hook global não funcionar corretamente no Linux, teste uma sessão X11/Xorg.

## Interface gráfica

Com o virtualenv ativo:

```bash
mousemover-gui
```

ou:

```bash
python -m mousemover.gui
```

Na GUI é possível escolher:

- monitor;
- plugin;
- intervalo;
- jitter mínimo/máximo;
- watchdog;
- sensor de mouse;
- execução única;
- modo sem console;
- ocultação da janela;
- reload de plugins.

## CLI

Menu interativo:

```bash
mousemover
```

Ajuda:

```bash
mousemover --help
```

Listar monitores:

```bash
mousemover --list-monitors
```

Listar plugins:

```bash
mousemover --list-plugins
```

Exemplo:

```bash
mousemover \
  --plugin nudge_inteligente \
  --monitor 0 \
  --interval 30 \
  --jitter-min 1 \
  --jitter-max 10 \
  --watchdog 3 \
  --daemon
```

Plugin humano:

```bash
mousemover \
  --plugin nudge_humano_30s \
  --monitor 0 \
  --interval 1 \
  --daemon
```

Com sensor que interrompe o loop quando o usuário mexer o mouse:

```bash
mousemover \
  --plugin nudge_inteligente \
  --mouse-hook \
  --interval 30 \
  --daemon
```

Executar um único ciclo:

```bash
mousemover --plugin basic --once
```

Ignorar `config.ini` e `config.json`:

```bash
mousemover \
  --force \
  --plugin nudge_inteligente \
  --monitor 0 \
  --interval 30 \
  --daemon
```

## Configuração JSON

`config.json` fornece defaults:

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

Prioridade:

```text
defaults do código
    ↓
config.json
    ↓
config.ini
    ↓
parâmetros CLI
```

`--force` ignora JSON e INI.

## INI

O `config.ini` é criado automaticamente para estado persistente da interface/menu, por exemplo:

```ini
[state]
monitor_index = 0
plugin = nudge_inteligente
mouse_hook = false
```

Ele não precisa ser distribuído.

## Plugins externos

Na primeira execução é criada a pasta:

```text
plugins/
```

ao lado do executável.

Um plugin externo deve conter:

```python
class MovementPlugin:
    name = "meu_plugin"

    def get_next_points(self, ctx):
        return [(ctx.current_x + 1, ctx.current_y)]
```

Na GUI clique em **Reload plugins**. No menu CLI use a opção de selecionar/recarregar plugins.

O plugin recebe `ctx` com:

```text
ctx.monitor
ctx.interval
ctx.jitter_min
ctx.jitter_max
ctx.last_user_activity
ctx.now
ctx.current_x
ctx.current_y
ctx.center_x
ctx.center_y
```

## Plugins incluídos

- `basic`
- `circle`
- `erosion`
- `fractal_walk`
- `nudge_diagonal_1px`
- `nudge_humano_30s`
- `nudge_inteligente`
- `nudge_noise_1px`
- `one_pixel_nudge`
- `random_walk`
- `spiral`
- `square`
- `zigzag`

### nudge_inteligente

Move 1 pixel em direção aleatória, validando se o destino pertence a algum monitor.

### nudge_humano_30s

Só gera movimento após 30 segundos sem movimento de mouse detectado. Recomenda-se:

```bash
mousemover --plugin nudge_humano_30s --interval 1 --daemon
```

## Logs

Arquivo:

```text
debug.log
```

Fica ao lado do programa. O arquivo não contém códigos ANSI; as cores são usadas apenas no terminal.

## Build Linux

O build Linux deve ser feito no Linux:

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

Resultado:

```text
dist/MouseMover
```

Uso:

```bash
./dist/MouseMover
```

Abre a GUI.

Com argumentos:

```bash
./dist/MouseMover --list-plugins
./dist/MouseMover --plugin nudge_inteligente --interval 30 --daemon
```

entra no modo CLI.

## Build Windows

Faça o build no Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
scripts\build_windows.bat
```

Resultado:

```text
dist\MouseMover.exe
```

### Um único EXE para GUI e CLI

Dê duplo clique:

```text
MouseMover.exe
```

e a interface gráfica é aberta.

No `cmd` ou PowerShell:

```bat
MouseMover.exe --help
MouseMover.exe --list-monitors
MouseMover.exe --list-plugins
MouseMover.exe --plugin nudge_inteligente --monitor 0 --interval 30 --daemon
```

o mesmo executável funciona como CLI.

No Windows, quando iniciado sem argumentos, o launcher oculta a janela de console e abre somente a GUI. Quando existem argumentos, o console é mantido para o modo CLI.

## Distribuição

O usuário final precisa baixar apenas:

```text
MouseMover.exe
```

ou, no Linux:

```text
MouseMover
```

Não é necessário instalar Python nem executar `pip`.

Na primeira utilização, o aplicativo pode criar ao lado do executável:

```text
debug.log
config.ini
plugins/
```

A pasta `plugins/` é opcional e existe para plugins `.py` externos.

## Desenvolvimento de plugins sem recompilar

Copie um `.py` para:

```text
plugins/
```

ao lado do executável.

Depois:

- GUI: clique em **Reload plugins**;
- CLI/menu: selecione a opção de plugins/reload.

Plugins externos com o mesmo `name` de um plugin interno substituem o interno naquela execução.

## Observações de plataforma

Tkinter é a interface padrão do Python para Tcl/Tk. No Linux, a instalação do pacote de sistema (`python3-tk` em Debian/Ubuntu) pode ser necessária durante o desenvolvimento.

A captura global de teclado/mouse depende do backend do sistema operacional. Em Linux, ambientes Wayland podem impor restrições; se necessário, teste em uma sessão X11/Xorg.

O executável deve ser validado no sistema operacional de destino. Para distribuição, gere o `.exe` no Windows e o binário Linux no Linux.
