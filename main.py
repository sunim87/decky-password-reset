import asyncio
import os
import pwd
from pathlib import Path

import decky


def target_user():
    # Only the account supplied by Decky, never a frontend-supplied username.
    name = decky.DECKY_USER
    account = pwd.getpwnam(name)
    if account.pw_uid < 1000 or any(c in name for c in ":\r\n\0"):
        raise ValueError("일반 사용자 계정을 확인할 수 없습니다.")
    return account.pw_name


def platform_name():
    try:
        values = {}
        for line in Path("/etc/os-release").read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep:
                values[key] = value.strip('"')
        identity = " ".join(values.get(k, "") for k in ("ID", "VARIANT_ID", "NAME", "IMAGE_ID")).lower()
        if "bazzite" in identity:
            return "Bazzite"
        if values.get("ID") == "steamos":
            return "SteamOS"
    except OSError:
        pass
    return None


def password_tool():
    return next((p for p in ("/usr/sbin/chpasswd", "/usr/bin/chpasswd", "/sbin/chpasswd") if os.path.isfile(p) and os.access(p, os.X_OK)), None)


class Plugin:
    async def get_status(self):
        try:
            user = target_user()
        except (KeyError, ValueError, AttributeError):
            return {"ready": False, "message": "Decky 사용자 계정을 확인할 수 없습니다."}
        system = platform_name()
        ready = os.geteuid() == 0 and system is not None and password_tool() is not None
        return {"ready": ready, "user": user, "system": system or "지원하지 않는 OS", "message": "준비됨" if ready else "SteamOS/Bazzite, root 권한 및 chpasswd가 필요합니다."}

    async def reset_password(self, password, confirmation):
        status = await self.get_status()
        if not status["ready"]:
            return {"ok": False, "message": status["message"]}
        if not isinstance(password, str) or not isinstance(confirmation, str) or password != confirmation:
            return {"ok": False, "message": "비밀번호가 일치하지 않습니다."}
        if not 4 <= len(password) <= 128 or any(c in password for c in "\r\n\0"):
            return {"ok": False, "message": "비밀번호는 4~128자이며 줄바꿈을 포함할 수 없습니다."}
        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                password_tool(), stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
            )
            await asyncio.wait_for(process.communicate(f"{target_user()}:{password}\n".encode()), timeout=20)
            if process.returncode != 0:
                return {"ok": False, "message": "변경에 실패했습니다. 비밀번호 정책이나 계정 상태를 확인하세요."}
            return {"ok": True, "message": "새 비밀번호를 설정했습니다."}
        except asyncio.TimeoutError:
            return {"ok": False, "message": "처리 시간이 초과되었습니다. 비밀번호 상태를 확인한 후 다시 시도하세요."}
        except OSError:
            return {"ok": False, "message": "비밀번호 변경 도구를 실행할 수 없습니다."}
        finally:
            if process is not None and process.returncode is None:
                process.kill()
                await process.wait()

    async def _main(self):
        pass

    async def _unload(self):
        pass
