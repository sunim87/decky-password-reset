# Decky Password Reset

SteamOS·Bazzite에서 **기존 비밀번호 없이 현재 사용자 계정에 새 비밀번호를 설정**하는 Decky Loader 플러그인입니다.

**이미 정상 작동하는 Decky Loader가 필요합니다.** 플러그인 백엔드가 Decky의 root 권한으로 실행됩니다. Decky가 없는 기기에서 관리자 권한을 얻거나 Decky 설치 과정의 인증을 대신하는 도구는 아닙니다.

## 다운로드와 설치

1. [최신 릴리스](https://github.com/sunim87/decky-password-reset/releases/latest)에서 `PasswordReset-0.1.6.zip`을 다운로드합니다. Source code ZIP은 설치 파일이 아닙니다.
2. Decky 설정의 개발자 모드를 켜고 ZIP 플러그인 설치 기능으로 해당 파일을 선택합니다. 메뉴 이름은 Decky 버전에 따라 다를 수 있습니다.
3. Decky 목록에서 **Password Reset**을 엽니다.
4. **비밀번호 재설정 창 열기**를 누르고 표시되는 OS와 대상 계정을 확인합니다.
5. 새 비밀번호와 확인란을 동일하게 입력하고 **재설정**을 누릅니다.
6. **새 비밀번호를 설정했습니다.** 메시지를 확인합니다.

최소 4자, 최대 128자를 입력할 수 있습니다. 실제 허용 여부는 시스템 비밀번호 정책에 따릅니다. 글자 수·비밀번호 일치 여부·계정 준비 상태에 따라 재설정 버튼이 활성화됩니다.

## 변경 범위와 권한

- Decky가 알려주는 `DECKY_USER` 계정을 감지하며 사용자 이름을 고정하지 않습니다.
- **사용자 로그인과 sudo에 사용하는 비밀번호가 함께 변경됩니다.** 새로운 sudo 사용 권한을 부여하지 않습니다.
- Steam 계정 비밀번호, 디스크 암호, KDE Wallet 비밀번호는 변경하지 않습니다. 기존 비밀번호로 잠긴 Wallet은 별도 처리가 필요할 수 있습니다.
- root 및 시스템 계정은 대상에서 제외합니다. 화면에서 임의의 사용자 이름을 지정할 수 없습니다.
- 시스템의 `chpasswd`를 사용하며 비밀번호를 명령 인자, 플러그인 파일 또는 플러그인 로그에 저장하지 않습니다.
- 기기를 조작해 플러그인을 실행할 수 있는 사람은 해당 계정의 비밀번호를 재설정할 수 있습니다.
- sudoers 변경, 영구적인 비밀번호 없는 sudo 설정, 별도 시스템 서비스 설치를 하지 않습니다.

## 확인된 기기

| 기기 | 운영체제 | 확인 내용 |
| --- | --- | --- |
| Steam Deck | SteamOS 3.9.6 | root 백엔드 로드, 플러그인 비밀번호 변경 후 SSH·sudo 인증 성공 |
| Lenovo Legion Go 2 | Bazzite 45 | root 백엔드 로드, 계정 감지, 플러그인 비밀번호 변경 후 SSH·sudo 인증 성공 |

v0.1.6 화면은 Steam 기본 확인 대화창을 사용합니다. 실기 인증 성공 확인과 별개로 모든 Steam 클라이언트 버전·화면 배율·키보드 조합을 보장하지 않습니다. 별도로 만든 데스크톱 스크립트의 테스트는 이 플러그인의 검증 범위에 포함하지 않습니다.

## 문제 해결

- **준비되지 않았다는 안내:** Decky의 root 실행, 지원 OS 및 `chpasswd` 존재 여부를 확인합니다.
- **재설정 버튼이 비활성화:** 안내 문구를 읽고 4~128자 및 두 입력값의 일치 여부를 확인합니다.
- **변경 실패:** 다른 비밀번호로 시도하고 계정 상태 및 시스템 정책을 확인합니다.
- **변경 확인:** 데스크톱 터미널에서 `sudo -k` 다음 `sudo -v`를 실행하고 새 비밀번호로 인증합니다. 입력 중 글자가 표시되지 않는 것은 정상입니다.

## 개발과 검증

Node.js 22 이상과 Python 3.11 이상을 사용합니다.

```sh
npm ci --ignore-scripts
npm run typecheck
npm run build
python -m unittest -v test_backend.py
python scripts/package_plugin.py
```

테스트는 OS와 계정 확인, 잘못된 입력 차단, 비밀번호의 표준 입력 전달, 시간 초과 처리를 모의 실행합니다. 실제 계정 비밀번호를 바꾸지 않습니다. 빌드 의존성에 npm audit 경고가 있으므로 배포자는 검토해야 합니다. `node_modules`와 빌드 도구는 설치 ZIP에 포함하지 않습니다.

이 저장소와 릴리스에는 Decky 플러그인만 포함합니다. 별도 데스크톱 sudo 설정 및 부팅 복구 스크립트는 포함하지 않습니다.

## 참고

- [Decky 공식 플러그인 템플릿](https://github.com/SteamDeckHomebrew/decky-plugin-template)
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader)

MIT License
