# Password Reset v0.1.6

SteamOS·Bazzite용 Decky 플러그인 첫 공개 릴리스입니다.

- 기존 비밀번호 없이 Decky 사용자 계정에 새 비밀번호 설정
- SteamOS·Bazzite 및 대상 계정 자동 감지
- 4~128자 입력, 확인 입력 및 준비 상태 안내
- Steam 기본 대화창으로 입력과 재설정을 한 화면에서 처리
- Steam Deck(SteamOS 3.9.6)·Legion Go 2(Bazzite 45)에서 플러그인 변경 후 SSH·sudo 인증 확인

이미 작동 중인 Decky Loader가 필요합니다. 사용자 로그인·sudo 비밀번호가 함께 변경되며 Steam 계정이나 디스크 암호는 바꾸지 않습니다. 기기를 조작해 이 플러그인을 실행할 수 있는 사람은 계정 비밀번호를 재설정할 수 있습니다.

**설치 파일은 아래 `PasswordReset-0.1.6.zip`입니다. Source code ZIP을 Decky에 설치하지 마세요.**

별도 데스크톱 스크립트, sudoers 설정, 복구 부팅 도구는 포함하지 않습니다.
