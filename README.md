<div align="center">

<img src="https://raw.githubusercontent.com/mainuan/.github/main/profile/assets/mainuan-logo.svg" width="96" alt="Logotipo do Mainuan">

# deb-manager-gui

Janela de progresso em Qt 6 para instalar ou remover pacotes APT e arquivos `.deb` chamados por outros programas.

[![CI](https://github.com/mainuan/deb-manager-gui/actions/workflows/ci.yml/badge.svg)](https://github.com/mainuan/deb-manager-gui/actions/workflows/ci.yml)
[![Licença](https://img.shields.io/github/license/mainuan/deb-manager-gui)](LICENSE)
![Plataforma](https://img.shields.io/badge/Kubuntu%2026.04%20%7C%20Plasma%206.6-0079c1)

**Português** · [English](README.en.md)

</div>

---

## O que é

O `deb-manager-gui` é um script Python com PyQt6 que executa operações de
pacote e mostra o andamento numa janela, sem terminal e sem cliques: a lista
de pacotes e a ação vêm da linha de comando. No fim, uma caixa de mensagem
informa sucesso ou erro.

Ele foi feito para ser chamado por outros programas, normalmente pelo
`pkexec`. O pacote não traz entrada de menu.

## Funcionalidades

- Instala (`--in`) e remove (`--rm`) um ou mais pacotes com `apt-get`.
- Instala um ou mais arquivos `.deb` locais (`--deb`) com `dpkg -i` e depois resolve as dependências que faltarem com `apt-get -f install`.
- Barra de progresso calculada a partir da saída do `apt-get` e do `dpkg`.
- Mensagem personalizada na janela com `--tx`.
- Operações sem perguntas interativas (`DEBIAN_FRONTEND=noninteractive`), mantendo os arquivos de configuração existentes (`--force-confdef`, `--force-confold`).
- Já como root (via `pkexec`), chama as ferramentas diretamente; como usuário comum, por `sudo`.
- Interface em 33 idiomas. Mesmo sob `pkexec`, que limpa o ambiente, usa o idioma da sessão Plasma de quem chamou (`~/.config/plasma-localerc`) ou o de `/etc/default/locale`.

## Instalação

O `deb-manager-gui` já vem na ISO do Mainuan Linux.

Ainda não há release versionada: a primeira será a **1.0.0** (versão já
registrada em `debian/changelog`), publicada com o `.deb` e o `SHA256SUMS`.
Até lá, gere o pacote a partir do código-fonte num Kubuntu/Ubuntu 26.04:

```bash
git clone https://github.com/mainuan/deb-manager-gui.git
cd deb-manager-gui
sudo apt build-dep ./
dpkg-buildpackage -us -uc -b
sudo apt install ../deb-manager-gui_1.0.0_all.deb
```

## Uso

```text
deb-manager-gui {--in | --rm} <pacote> [pacote ...] [--tx <mensagem>]
deb-manager-gui --deb <arquivo.deb> [arquivo.deb ...] [--tx <mensagem>]
```

| Opção | Efeito |
|---|---|
| `--in` | instala os pacotes indicados dos repositórios APT configurados |
| `--rm` | remove os pacotes indicados |
| `--deb` | instala arquivos `.deb` locais e resolve as dependências com `apt-get -f install` |
| `--tx MENSAGEM` | texto mostrado na janela no lugar da lista de pacotes; tudo o que vem depois de `--tx` faz parte da mensagem |

Exemplos:

```bash
pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY deb-manager-gui --in htop neofetch
pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY deb-manager-gui --rm htop
pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY deb-manager-gui --deb ./google-chrome-stable_current_amd64.deb
pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY deb-manager-gui --in rar zip --tx "Instalando descompactadores"
```

O `pkexec` limpa o ambiente; por isso `DISPLAY` e `XAUTHORITY` são repassados
com `env` para que a janela possa abrir na sessão gráfica.

Sem argumentos, o programa mostra a forma de uso e termina. Página de manual:
`man deb-manager-gui`.

## Informações técnicas

| Item | Valor |
|---|---|
| Linguagem | Python 3 (um único script, `/usr/bin/deb-manager-gui`) |
| Toolkit | Qt 6 (PyQt6) |
| Base | Kubuntu 26.04 LTS, KDE Plasma 6.6 |
| Pacote | `deb-manager-gui`, `Architecture: all` |
| Dependências | `apt`, `python3`, `python3-pyqt6`; recomenda `pkexec` e `sudo` |
| Privilégios | root via `pkexec` (quem chama), ou `sudo` |
| Arquitetura do sistema | amd64 |

## Compilação e testes

```bash
sudo apt build-dep ./
dpkg-buildpackage -us -uc -b      # gera ../deb-manager-gui_<versão>_all.deb
```

A versão vem de `debian/changelog`. Durante o build, o `debian/rules` executa
`tests/test_i18n.py` e `tests/test_worker.py`. Antes dele, o CI executa:

```bash
po/i18n.sh check-pot && po/i18n.sh validate
```

O workflow [`CI`](.github/workflows/ci.yml) usa o pipeline Debian comum da
organização: build num contêiner Ubuntu 26.04 fixado por digest, `lintian`,
`SHA256SUMS`, instalação num Ubuntu 26.04 limpo, teste de fumaça (mensagem de
uso em português e inglês e catálogos instalados), reinstalação e remoção. A
release só é publicada por uma tag `v*`.

## Traduções

Catálogos gettext em `po/` (domínio `deb-manager-gui`, textos-fonte em
inglês), em 33 idiomas listados em `po/LINGUAS`. Como contribuir:
[docs/i18n/README.md](docs/i18n/README.md).

## Contribuição

Relate problemas em [Issues](https://github.com/mainuan/deb-manager-gui/issues)
e envie mudanças por pull request para `main`. O
[CI](https://github.com/mainuan/deb-manager-gui/actions/workflows/ci.yml)
precisa estar verde.

## Créditos

- Charles Santana ([@selrahcsan](https://github.com/selrahcsan)): autor.
- Rafael Ruscher ([@ruscher](https://github.com/ruscher)): internacionalização, empacotamento Debian e CI.

## Licença

[MIT](LICENSE), Copyright (c) 2025 Charles Santana.
