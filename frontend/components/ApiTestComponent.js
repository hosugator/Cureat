import React, { useState } from 'react';
import { View, Text, Button, Alert, StyleSheet, ScrollView } from 'react-native';
import { login, signup } from '../services/authService';
import { search, createDateCourse } from '../services/searchService';
import { API_BASE_URL } from '../services/networkConfig';

export default function ApiTestComponent() {
  const [testResult, setTestResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const testAuthService = async () => {
    setIsLoading(true);
    try {
      console.log('Auth Service 테스트 시작...');
      
      // 로그인 테스트
      const loginResult = await login('test@example.com', 'password123');
      console.log('로그인 테스트 결과:', loginResult);
      
      // 회원가입 테스트 데이터
      const signupData = {
        name: "테스트 사용자",
        birthdate: "1995-10-24",
        gender: "남자",
        email: "testuser@example.com",
        phone: "01012345678",
        address: "서울시 강남구 테헤란로",
        interests: "데이트, 회식",
        allergies: false,
        password: "testpass123!"
      };
      
      const signupResult = await signup(signupData);
      console.log('회원가입 테스트 결과:', signupResult);
      
      setTestResult('Auth Service 테스트 성공!\n로그인: ' + JSON.stringify(loginResult, null, 2) + '\n회원가입: ' + JSON.stringify(signupResult, null, 2));
      Alert.alert('성공', 'Auth Service 테스트가 완료되었습니다.');
      
    } catch (error) {
      console.error('Auth Service 테스트 오류:', error);
      setTestResult('Auth Service 테스트 실패: ' + error.message);
      Alert.alert('오류', 'Auth Service 테스트 실패: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const testSearchService = async () => {
    setIsLoading(true);
    try {
      console.log('Search Service 테스트 시작...');
      
      // 추천 검색 테스트
      const searchResult = await search('강남 맛집 추천', 1);
      console.log('검색 테스트 결과:', searchResult);
      
      // 데이트 코스 생성 테스트
      const courseData = {
        user_id: 1,
        location: "서울 강남역",
        start_time: "14:00",
        end_time: "20:00",
        theme: "로맨틱 데이트"
      };
      
      const courseResult = await createDateCourse(courseData);
      console.log('데이트 코스 생성 테스트 결과:', courseResult);
      
      setTestResult('Search Service 테스트 성공!\n검색: ' + JSON.stringify(searchResult, null, 2) + '\n코스: ' + JSON.stringify(courseResult, null, 2));
      Alert.alert('성공', 'Search Service 테스트가 완료되었습니다.');
      
    } catch (error) {
      console.error('Search Service 테스트 오류:', error);
      setTestResult('Search Service 테스트 실패: ' + error.message);
      Alert.alert('오류', 'Search Service 테스트 실패: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const testNetworkConnection = async () => {
    setIsLoading(true);
    try {
      console.log('네트워크 연결 테스트 시작...');
      
      const response = await fetch(`${API_BASE_URL}/test`);
      const data = await response.json();
      
      console.log('네트워크 테스트 결과:', data);
      setTestResult('네트워크 연결 테스트 성공!\n' + JSON.stringify(data, null, 2));
      Alert.alert('성공', '백엔드 서버와 연결되었습니다.');
      
    } catch (error) {
      console.error('네트워크 테스트 오류:', error);
      setTestResult('네트워크 연결 실패: ' + error.message);
      Alert.alert('오류', '네트워크 연결 실패: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>API 연결 테스트</Text>
      
      <View style={styles.buttonContainer}>
        <Button
          title="네트워크 연결 테스트"
          onPress={testNetworkConnection}
          disabled={isLoading}
        />
      </View>
      
      <View style={styles.buttonContainer}>
        <Button
          title="Auth Service 테스트"
          onPress={testAuthService}
          disabled={isLoading}
        />
      </View>
      
      <View style={styles.buttonContainer}>
        <Button
          title="Search Service 테스트"
          onPress={testSearchService}
          disabled={isLoading}
        />
      </View>
      
      {isLoading && <Text style={styles.loading}>테스트 중...</Text>}
      
      {testResult && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>테스트 결과:</Text>
          <Text style={styles.resultText}>{testResult}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  buttonContainer: {
    marginVertical: 10,
  },
  loading: {
    textAlign: 'center',
    marginVertical: 20,
    fontSize: 16,
    color: '#666',
  },
  resultContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  resultText: {
    fontSize: 12,
    fontFamily: 'monospace',
  },
});