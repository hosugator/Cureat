import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator, SafeAreaView, KeyboardAvoidingView, Platform } from 'react-native';
import { Link, useRouter } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import { login as authLogin } from '../../services/authService';

export default function LoginScreen() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();
    const { setToken } = useAuth(); // setToken 함수를 가져옵니다.

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert('입력 오류', '이메일과 비밀번호를 모두 입력해주세요.');
            return;
        }
        setIsLoading(true);
        try {
            // authService.login 호출하여 토큰 받기
            const response = await authLogin(email, password);
            console.log("로그인 성공 응답:", response);
            if (response && response.access_token) {
                // AuthContext의 setToken 함수에 액세스 토큰을 전달합니다.
                setToken(response.access_token);
                // 로그인 성공 후 홈 화면으로 이동
                router.replace('/home');
            } else {
                 Alert.alert('로그인 실패', '서버 응답이 올바르지 않습니다.');
            }
        } catch (error) {
            console.error("로그인 중 오류 발생:", error);
            Alert.alert('로그인 실패', error.message || '알 수 없는 오류가 발생했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView 
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
      >
        <Text style={styles.title}>Cureat</Text>
        <Text style={styles.subtitle}>AI와 함께하는 미식의 순간</Text>
        
        <TextInput
            style={styles.input}
            placeholder="이메일"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
        />
        <TextInput
            style={styles.input}
            placeholder="비밀번호"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
        />

        <TouchableOpacity 
            style={styles.loginButton}
            onPress={handleLogin}
            disabled={isLoading}
        >
            {isLoading ? (
                <ActivityIndicator color="#fff" />
            ) : (
                <Text style={styles.loginButtonText}>로그인</Text>
            )}
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: '#fff',
    },
    container: {
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 24,
    },
    title: {
        fontSize: 48,
        fontWeight: 'bold',
        color: '#EC4899', // text-pink-500
        textAlign: 'center',
    },
    subtitle: {
        fontSize: 16,
        color: '#6B7280', // text-gray-500
        textAlign: 'center',
        marginBottom: 48,
    },
    input: {
        height: 50,
        borderColor: '#E5E7EB', // border-gray-200
        borderWidth: 1,
        borderRadius: 12,
        paddingHorizontal: 16,
        marginBottom: 16,
        fontSize: 16,
    },
    loginButton: {
        backgroundColor: '#EC4899', // bg-pink-500
        height: 50,
        borderRadius: 12,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 8,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },

});
