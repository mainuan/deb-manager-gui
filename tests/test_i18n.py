#!/usr/bin/env python3
"""Teste de i18n: executa o código real do deb-manager-gui com LANGUAGE=pt_BR e
LANGUAGE=en e verifica os textos da janela, do QMessageBox e do uso (--help).

Nenhum comando apt/dpkg/sudo é executado: o AptWorker é substituído por um falso.
Executar: python3 tests/test_i18n.py   (requer PyQt6 e GNU gettext/msgfmt)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "deb-manager-gui")

PROBE = r'''
import json, sys
from importlib.machinery import SourceFileLoader
import importlib.util
loader = SourceFileLoader("dmg", sys.argv[1])
spec = importlib.util.spec_from_loader("dmg", loader)
dmg = importlib.util.module_from_spec(spec)
loader.exec_module(dmg)
from PyQt6.QtWidgets import QApplication, QMessageBox

class FakeWorker:
    def __init__(self, packages, mode): pass
    class _Sig:
        def connect(self, *a): pass
    progress = _Sig(); finished = _Sig()
    def start(self): pass

dmg.AptWorker = FakeWorker
shown = []
QMessageBox.information = lambda parent, title, text: shown.append([title, text])
QMessageBox.critical = lambda parent, title, text: shown.append([title, text])
app = QApplication([])
out = {}
w = dmg.ManagerWindow(["htop", "vim"], "install")
out["install_title"] = w.windowTitle(); out["install_label"] = w.label.text()
w.on_finished(True, "htop, vim"); w.on_finished(False, dmg._("File not found: {path}").format(path="x.deb"))
w2 = dmg.ManagerWindow(["htop"], "remove")
out["remove_title"] = w2.windowTitle(); out["remove_label"] = w2.label.text()
w2.on_finished(True, "htop")
out["boxes"] = shown
print(json.dumps(out, ensure_ascii=False))
'''

# Runs the real main() with an empty Qt translations directory (no qtbase_<lang>.qm).
DIRECTION_PROBE = r'''
import json, sys, tempfile
from importlib.machinery import SourceFileLoader
import importlib.util
from unittest import mock
loader = SourceFileLoader("dmg", sys.argv[1])
spec = importlib.util.spec_from_loader("dmg", loader)
dmg = importlib.util.module_from_spec(spec)
loader.exec_module(dmg)

class FakeWorker:
    def __init__(self, packages, mode): pass
    class _Sig:
        def connect(self, *a): pass
    progress = _Sig(); finished = _Sig()
    def start(self): pass

dmg.AptWorker = FakeWorker
out = {}

def fake_exec(app):
    out["direction"] = app.layoutDirection().name
    out["window_rtl"] = [w.isRightToLeft() for w in app.topLevelWidgets() if isinstance(w, dmg.ManagerWindow)]
    out["title"] = [w.windowTitle() for w in app.topLevelWidgets() if isinstance(w, dmg.ManagerWindow)]
    return 0

with tempfile.TemporaryDirectory() as empty, \
        mock.patch.object(dmg.QLibraryInfo, "path", return_value=empty), \
        mock.patch.object(dmg.QApplication, "exec", fake_exec), \
        mock.patch.object(sys, "argv", ["deb-manager-gui", "--in", "htop"]):
    try:
        dmg.main()
    except SystemExit:
        pass
print(json.dumps(out, ensure_ascii=False))
'''


class I18nTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import PyQt6.QtWidgets  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("PyQt6 não disponível")
        cls.tmp = tempfile.mkdtemp()
        subprocess.run([os.path.join(ROOT, "po", "i18n.sh"), "compile", cls.tmp], check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def env(self, language):
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen", DEB_MANAGER_GUI_LOCALEDIR=self.tmp)
        for var in ("LC_ALL", "LC_MESSAGES"):
            env.pop(var, None)
        env["LANG"] = "C.UTF-8" if language in ("C", "en") else "pt_BR.UTF-8"
        env["LANGUAGE"] = language
        return env

    def probe(self, language):
        r = subprocess.run([sys.executable, "-c", PROBE, SCRIPT], env=self.env(language),
                           capture_output=True, text=True, check=True)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def usage(self, language):
        r = subprocess.run([sys.executable, SCRIPT], env=self.env(language),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        return r.stdout

    def test_pt_BR(self):
        o = self.probe("pt_BR")
        self.assertEqual(o["install_title"], "Instalando Pacotes")
        self.assertEqual(o["install_label"], "Instalando: htop, vim")
        self.assertEqual(o["remove_title"], "Removendo Pacotes")
        self.assertEqual(o["remove_label"], "Removendo: htop")
        self.assertEqual(o["boxes"], [
            ["Sucesso", "htop, vim instalados com sucesso!"],
            ["Erro", "Falha: Arquivo não encontrado: x.deb"],
            ["Sucesso", "htop removidos com sucesso!"],
        ])
        self.assertEqual(self.usage("pt_BR"),
                         "Uso:\n  --in <pacote1> [pacote2 ...]\n  --rm <pacote1> [pacote2 ...]\n"
                         "  --deb <arquivo1.deb> [arquivo2.deb ...]\n  [--tx mensagem personalizada]\n")

    def test_english(self):
        for language in ("en", "C"):
            o = self.probe(language)
            self.assertEqual(o["install_title"], "Installing Packages")
            self.assertEqual(o["install_label"], "Installing: htop, vim")
            self.assertEqual(o["remove_title"], "Removing Packages")
            self.assertEqual(o["boxes"], [
                ["Success", "htop, vim installed successfully!"],
                ["Error", "Failed: File not found: x.deb"],
                ["Success", "htop removed successfully!"],
            ])
            self.assertEqual(self.usage(language),
                             "Usage:\n  --in <package1> [package2 ...]\n  --rm <package1> [package2 ...]\n"
                             "  --deb <file1.deb> [file2.deb ...]\n  [--tx custom message]\n")

    def direction(self, language):
        r = subprocess.run([sys.executable, "-c", DIRECTION_PROBE, SCRIPT], env=self.env(language),
                           capture_output=True, text=True, check=True)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_right_to_left_catalog_mirrors_without_qtbase(self):
        # The application's Arabic catalog is used: mirrored even without qtbase_ar.
        o = self.direction("ar")
        self.assertEqual(o["direction"], "RightToLeft")
        self.assertEqual(o["window_rtl"], [True])
        # Urdu has an application catalog but no qtbase_ur: mirrored by the catalog.
        o = self.direction("ur")
        self.assertEqual(o["direction"], "RightToLeft")
        self.assertEqual(o["window_rtl"], [True])
        # Yiddish is right-to-left but has no application catalog: English, left to right.
        o = self.direction("yi")
        self.assertEqual(o["title"], ["Installing Packages"])
        self.assertEqual(o["direction"], "LeftToRight")
        self.assertEqual(o["window_rtl"], [False])


class CallerLanguageTest(unittest.TestCase):
    """pkexec limpa o ambiente: o idioma vem do Plasma de quem chamou."""

    @classmethod
    def setUpClass(cls):
        try:
            import PyQt6.QtWidgets  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("PyQt6 não disponível")
        from importlib.machinery import SourceFileLoader
        import importlib.util
        loader = SourceFileLoader("dmg_language", SCRIPT)
        spec = importlib.util.spec_from_loader("dmg_language", loader)
        cls.dmg = importlib.util.module_from_spec(spec)
        loader.exec_module(cls.dmg)

    def run_with(self, environ, localerc=None, default_locale=None):
        from unittest import mock
        import types
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, True)
        if localerc is not None:
            os.makedirs(os.path.join(home, ".config"))
            with open(os.path.join(home, ".config", "plasma-localerc"), "w", encoding="utf-8") as f:
                f.write(localerc)
        etc = os.path.join(home, "default-locale")
        if default_locale is not None:
            with open(etc, "w", encoding="utf-8") as f:
                f.write(default_locale)
        with mock.patch.object(self.dmg.pwd, "getpwuid", return_value=types.SimpleNamespace(pw_dir=home)):
            self.dmg._inherit_caller_language(environ, etc)
        return environ

    def test_plasma_language_of_the_caller(self):
        env = self.run_with({"PKEXEC_UID": "1000"},
                            "[Formats]\nLANG=de_DE.UTF-8\n\n[Translations]\nLANGUAGE=de:en_US\n")
        self.assertEqual(env["LANGUAGE"], "de:en_US")
        self.assertEqual(env["LANG"], "de_DE.UTF-8")

    def test_system_default_when_plasma_has_no_language(self):
        env = self.run_with({"PKEXEC_UID": "1000"}, None, 'LANG="fr_FR.UTF-8"\n')
        self.assertEqual(env, {"PKEXEC_UID": "1000", "LANG": "fr_FR.UTF-8"})

    def test_existing_language_and_non_pkexec_runs_are_untouched(self):
        rc = "[Translations]\nLANGUAGE=ja\n"
        self.assertEqual(self.run_with({"PKEXEC_UID": "1000", "LANGUAGE": "pt_BR"}, rc),
                         {"PKEXEC_UID": "1000", "LANGUAGE": "pt_BR"})
        self.assertEqual(self.run_with({}, rc), {})

    def test_unsafe_values_are_ignored(self):
        env = self.run_with({"PKEXEC_UID": "1000"}, "[Translations]\nLANGUAGE=de; rm -rf /\n")
        self.assertNotIn("LANGUAGE", env)


if __name__ == "__main__":
    unittest.main(verbosity=2)
