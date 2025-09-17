// frontend/app/home/index.js

import React from 'react';
import { useRouter } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import HomeUI from '../../components/HomeUI';
import { Alert } from 'react-native';

export default function HomeScreen() {
  const router = useRouter();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    router.replace('/login');
  };

  // 검색어를 ResultScreen으로 전달합니다.
  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      Alert.alert('알림', '검색어를 입력해주세요.');
      return;
    }
    // ResultScreen으로 이동하며 검색어를 파라미터로 전달합니다.
    router.push({
      pathname: '/search',
      params: { initialQuery: searchQuery }
    });
  };

  return <HomeUI handleLogout={handleLogout} handleSearch={handleSearch} />;
}
