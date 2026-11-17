#!/usr/bin/env python3
"""Testes do AptWorker sem executar apt/dpkg: marcadores de progresso,
ambiente das ferramentas e linha de comando privilegiada."""
import importlib.util
import os
import unittest
from importlib.machinery import SourceFileLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_loader = SourceFileLoader("dmg_worker", os.path.join(ROOT, "deb-manager-gui"))
_spec = importlib.util.spec_from_loader("dmg_worker", _loader)
dmg = importlib.util.module_from_spec(_spec)
_loader.exec_module(dmg)


class ProgressMarkerTest(unittest.TestCase):
    def test_english_apt_output(self):
        self.assertEqual(dmg._progress_marker("Reading package lists... Done"), 10)
        self.assertEqual(dmg._progress_marker("Building dependency tree... Done"), 20)
        self.assertEqual(dmg._progress_marker("Reading state information... Done"), 30)
        self.assertEqual(dmg._progress_marker("Unpacking hello (2.10-5) ..."), 60)
        self.assertEqual(dmg._progress_marker("Removing hello (2.10-5) ..."), 60)
        self.assertEqual(dmg._progress_marker("Setting up hello (2.10-5) ..."), 90)

    def test_unrelated_line(self):
        self.assertEqual(dmg._progress_marker("Get:1 http://archive.ubuntu.com"), 0)


class EnvironmentTest(unittest.TestCase):
    def test_messages_in_c_locale_without_prompts(self):
        env = dmg._package_tool_environment(
            {"LANGUAGE": "pt_BR", "LC_ALL": "pt_BR.UTF-8", "LANG": "pt_BR.UTF-8", "PATH": "/usr/bin"})
        self.assertEqual(env["LC_ALL"], "C.UTF-8")
        self.assertNotIn("LANGUAGE", env)
        self.assertEqual(env["DEBIAN_FRONTEND"], "noninteractive")
        self.assertEqual(env["PATH"], "/usr/bin")


class PrivilegedCommandTest(unittest.TestCase):
    def test_root_runs_directly(self):
        cmd = dmg._privileged(["apt-get", "install", "-y", "hello"], euid=0)
        self.assertEqual(cmd[0], "apt-get")
        self.assertIn("Dpkg::Options::=--force-confold", cmd)
        self.assertEqual(cmd[-3:], ["install", "-y", "hello"])

    def test_user_goes_through_sudo(self):
        cmd = dmg._privileged(["dpkg", "-i", "x.deb"], euid=1000)
        self.assertEqual(cmd[:2], ["sudo", "dpkg"])
        self.assertIn("--force-confold", cmd)


if __name__ == "__main__":
    unittest.main()
