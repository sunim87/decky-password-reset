"""Mock-only tests: never execute a real password command."""
import importlib.util
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

sys.modules.setdefault("pwd", types.SimpleNamespace(getpwnam=lambda name: types.SimpleNamespace(pw_uid=1000, pw_name=name)))
sys.modules["decky"] = types.SimpleNamespace(DECKY_USER="handheld")
spec = importlib.util.spec_from_file_location("backend", "main.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class BackendTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.plugin = backend.Plugin()
        self.plugin.get_status = AsyncMock(return_value={"ready": True})

    async def test_invalid_passwords_never_start_process(self):
        with patch.object(backend.asyncio, "create_subprocess_exec", new_callable=AsyncMock) as spawn:
            for password, confirmation in [("", ""), ("123", "123"), ("password1", "different"), ("abcdefgh\nroot:bad", "abcdefgh\nroot:bad"), ("x" * 129, "x" * 129)]:
                self.assertFalse((await self.plugin.reset_password(password, confirmation))["ok"])
            spawn.assert_not_called()

    async def test_not_ready_does_not_spawn(self):
        self.plugin.get_status.return_value = {"ready": False, "message": "blocked"}
        with patch.object(backend.asyncio, "create_subprocess_exec", new_callable=AsyncMock) as spawn:
            self.assertFalse((await self.plugin.reset_password("password1", "password1"))["ok"])
            spawn.assert_not_called()

    async def test_password_only_in_stdin(self):
        process = types.SimpleNamespace(returncode=0, communicate=AsyncMock())
        with patch.object(backend, "password_tool", return_value="/usr/bin/chpasswd"), patch.object(backend, "target_user", return_value="handheld"), patch.object(backend.asyncio, "create_subprocess_exec", new_callable=AsyncMock, return_value=process) as spawn:
            self.assertTrue((await self.plugin.reset_password("1234", "1234"))["ok"])
            self.assertEqual(spawn.call_args.args, ("/usr/bin/chpasswd",))
            process.communicate.assert_awaited_once_with(b"handheld:1234\n")

    async def test_timeout_kills_process(self):
        from unittest.mock import Mock
        process = types.SimpleNamespace(returncode=None, communicate=AsyncMock(side_effect=backend.asyncio.TimeoutError), kill=Mock(), wait=AsyncMock())
        with patch.object(backend, "password_tool", return_value="/usr/bin/chpasswd"), patch.object(backend, "target_user", return_value="handheld"), patch.object(backend.asyncio, "create_subprocess_exec", new_callable=AsyncMock, return_value=process):
            self.assertFalse((await self.plugin.reset_password("password1", "password1"))["ok"])
            process.kill.assert_called_once()

    async def test_root_target_rejected(self):
        with patch.object(backend.pwd, "getpwnam", return_value=types.SimpleNamespace(pw_uid=0, pw_name="root")):
            with self.assertRaises(ValueError):
                backend.target_user()

    async def test_supported_systems(self):
        for release, expected in [('ID=steamos\n', 'SteamOS'), ('ID=fedora\nNAME="Bazzite"\n', 'Bazzite'), ('ID=ubuntu\n', None)]:
            with patch.object(backend.Path, "read_text", return_value=release):
                self.assertEqual(backend.platform_name(), expected)


if __name__ == "__main__":
    unittest.main()
