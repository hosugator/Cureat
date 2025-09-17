프런트엔드 프로젝트 요구사항
1. 프로젝트 개요
이 프로젝트는 "Cureat"의 프런트엔드 애플리케이션으로, React Native와 Expo를 기반으로 개발되었습니다. 현재는 사용자 인증(로그인/로그아웃) 및 주요 화면(랜딩, 로그인, 홈)의 초기 UI가 구현되었습니다.

2. 필수 조건
프로젝트를 실행하려면 다음 소프트웨어가 설치되어 있어야 합니다.

Node.js: v18.0.0 이상

npm: v8.0.0 이상

Yarn: v1.22.0 이상 (권장)

Expo CLI: v6.0.0 이상

npm install --global expo-cli

3. 의존성 목록
프로젝트에 필요한 패키지 목록입니다. npm install 또는 yarn install을 실행하면 자동으로 설치됩니다.

expo

expo-router

expo-status-bar

react

react-native

react-native-safe-area-context

react-native-screens

@react-native-async-storage/async-storage

4. 설치 및 실행 방법
프로젝트 클론:

git clone [깃허브 저장소 주소]
cd frontend

의존성 설치:

npm install
# 또는
yarn install

Expo 애플리케이션 실행:

npm start
# 또는
yarn start

QR 코드가 나타나면 Expo Go 앱으로 스캔하여 기기에서 실행할 수 있습니다.

5. 현재 구현된 기능
토큰 기반 로그인: AsyncStorage를 사용하여 토큰을 저장하고 로그인 상태를 유지합니다.

동적 라우팅: 로그인 상태에 따라 초기 화면이 랜딩 페이지 또는 홈 화면으로 자동 전환됩니다.

로그아웃: 홈 화면의 로그아웃 버튼을 통해 토큰이 삭제되고 로그인 화면으로 돌아갑니다.

홈 화면 UI: 제공된 디자인 시안에 따라 홈 화면의 UI가 구현되었습니다 (더미 데이터 사용).