import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 1. Context 생성
const AuthContext = createContext();

// 2. Provider 컴포넌트
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(null); // 초기 상태는 null로 설정하여 로딩 중임을 나타냅니다.
  const [user, setUser] = useState(null);

  useEffect(() => {
    // 앱 시작 시 로컬 스토리지에서 토큰을 불러오는 함수
    const loadToken = async () => {
      try {
        const storedToken = await AsyncStorage.getItem('userToken');
        if (storedToken) {
          // TODO: 실제 프로젝트에서는 토큰의 유효성을 서버에 검증하는 로직이 필요합니다.
          // 지금은 토큰이 있으면 로그인된 상태로 간주합니다.
          setIsLoggedIn(true);
          setUser({ username: '사용자' }); // 실제 앱에서는 토큰을 디코딩하여 유저 정보를 얻어야 합니다.
        } else {
          setIsLoggedIn(false);
        }
      } catch (e) {
        console.error('Failed to load token from storage', e);
        setIsLoggedIn(false);
      }
    };

    loadToken();
  }, []);

  const login = async (userData) => {
    try {
      // 백엔드에서 반환하는 access_token을 사용
      const token = userData.access_token || userData.token;
      
      if (!token) {
        throw new Error('토큰이 없습니다.');
      }
      
      await AsyncStorage.setItem('userToken', token);
      setIsLoggedIn(true);
      // user 정보가 없으면 기본값 설정
      setUser(userData.user || { username: '사용자' });
    } catch (e) {
      console.error('Failed to save token to storage', e);
      throw e; // 에러를 다시 던져서 호출하는 곳에서 처리할 수 있도록 함
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('userToken');
      setIsLoggedIn(false);
      setUser(null);
    } catch (e) {
      console.error('Failed to remove token from storage', e);
    }
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// 3. 커스텀 훅
export const useAuth = () => useContext(AuthContext);
