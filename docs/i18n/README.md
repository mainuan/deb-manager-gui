# Internacionalização (i18n) do deb-manager-gui

* **Domínio gettext:** `deb-manager-gui` (nome do pacote Debian).
* **Idioma-fonte:** inglês (`msgid`); a interface brasileira está em `po/pt_BR.po`.
* **API:** `gettext.translation(TEXTDOMAIN, localedir, fallback=True)` no próprio
  script; placeholders `{nome}` com `.format()`. Os botões padrão do Qt
  (`QMessageBox`) vêm de `qtbase_<lang>.qm`, carregado para `QLocale.system()`.
* **Idioma:** nunca forçado; segue `LANGUAGE`/`LC_ALL`/`LC_MESSAGES`/`LANG`.

## Layout

```
po/i18n.sh            script padrão Mainuan (extract/update/validate/check-pot/compile)
po/i18n.conf          DOMAIN=deb-manager-gui
po/POTFILES.in        [Python] deb-manager-gui
po/LINGUAS            idiomas instalados (hoje só pt_BR)
po/deb-manager-gui.pot modelo (versionado)
po/pt_BR.po
tests/test_i18n.py    teste automático (pt_BR e en/C)
```

## Onde os catálogos são procurados

1. `$DEB_MANAGER_GUI_LOCALEDIR`, se definida;
2. `./build/locale` ao lado do script (execução a partir do código-fonte);
3. `/usr/share/locale` (pacote instalado).

## Tarefas

```bash
po/i18n.sh extract        # após mudar textos no código
po/i18n.sh update         # mescla o POT nos .po
po/i18n.sh validate       # msgfmt --check + placeholders
po/i18n.sh check-pot      # falha se o POT estiver desatualizado (CI)
po/i18n.sh add es         # novo idioma (Plural-Forms verificado)
po/i18n.sh compile build/locale
LANGUAGE=en ./deb-manager-gui --in htop      # testar em inglês
QT_QPA_PLATFORM=offscreen python3 tests/test_i18n.py
```

## Empacotamento

O workflow `.github/workflows/deb-manager-release.yml` roda `check-pot`, `validate`
e o teste, e instala os `.mo` com
`po/i18n.sh compile deb-manager-pkg/usr/share/locale`. Não há `.desktop` neste
repositório.

## Particularidades

* As palavras procuradas na saída do `apt` (`"Lendo listas"`, `"Instalando"`,
  `"Configurando"`…) servem só para estimar o progresso e **não** são traduzidas;
  com o apt em outro idioma o progresso avança apenas por pacote (comportamento
  anterior mantido).
* O texto de `--tx` é fornecido por quem chama o programa e é exibido como veio.
* O programa costuma rodar via `pkexec`, que limpa o ambiente. Se nenhuma
  variável de idioma chegar e `PKEXEC_UID` estiver definido, ele usa o idioma que
  o usuário que o chamou escolheu no Plasma (`~/.config/plasma-localerc`,
  `[Translations] LANGUAGE` e `[Formats] LANG`) e, na falta dele,
  `/etc/default/locale`. Repassar `LANGUAGE`/`LANG` explicitamente continua
  tendo prioridade.
* `po/i18n.sh` local usa uma única tag `--add-comments` (`Translators:`): o
  xgettext só respeita a última tag passada.
