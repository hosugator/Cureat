import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router'; // useRouter를 임포트합니다.

const SocialButton = ({ title, icon, backgroundColor, textColor, borderColor, onPress }) => (
    <TouchableOpacity
        style={[styles.socialButton, { backgroundColor: backgroundColor, borderColor: borderColor }]}
        onPress={onPress}
    >
        <Text style={[styles.socialButtonIcon, { color: textColor }]}>{icon}</Text>
        <Text style={[styles.socialButtonText, { color: textColor }]}>{title}</Text>
    </TouchableOpacity>
);

const LoginButton = ({ title, backgroundColor, textColor, borderColor, onPress }) => (
    <TouchableOpacity
        style={[styles.loginButton, { backgroundColor: backgroundColor, borderColor: borderColor }]}
        onPress={onPress}
    >
        <Text style={[styles.loginButtonText, { color: textColor }]}>{title}</Text>
    </TouchableOpacity>
);

export default function LoginPage() {
    const router = useRouter(); // useRouter 훅을 사용합니다.

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Cureat</Text>
                <Text style={styles.description}>
                    음식의 맛을 넘어, 경험의 맛까지
                </Text>
                <Text style={styles.description}>
                    AI 기반 추천으로 완성하는 특별한 식사 경험
                </Text>
            </View>

            <View style={styles.socialButtonsContainer}>
                <SocialButton
                    title="카카오로 시작하기"
                    icon="💬"
                    backgroundColor="#FEE500"
                    textColor="#191919"
                    borderColor="#FEE500"
                />
                <SocialButton
                    title="Apple로 시작하기"
                    icon=""
                    backgroundColor="#000000"
                    textColor="#FFFFFF"
                    borderColor="#000000"
                />
                <SocialButton
                    title="네이버로 시작하기"
                    icon="N"
                    backgroundColor="#03C75A"
                    textColor="#FFFFFF"
                    borderColor="#03C75A"
                />
                <SocialButton
                    title="Google로 시작하기"
                    icon="G"
                    backgroundColor="#FFFFFF"
                    textColor="#191919"
                    borderColor="#CCCCCC"
                />
            </View>
            <View style={styles.separatorContainer}>
                <View style={styles.separatorLine} />
                <Text style={styles.separatorText}>또는</Text>
                <View style={styles.separatorLine} />
            </View>

            <View style={styles.authButtonsContainer}>
                <LoginButton
                    title="아이디로 로그인"
                    backgroundColor="#FFFFFF"
                    textColor="#191919"
                    borderColor="#CCCCCC"
                    onPress={() => router.push('login/')} // 경로를 login/login으로 변경합니다.
                />
                <LoginButton
                    title="회원가입"
                    backgroundColor="#FFFFFF"
                    textColor="#191919"
                    borderColor="#CCCCCC"
                    onPress={() => console.log('회원가입 버튼 클릭')}
                />
            </View>

            <View style={styles.footer}>
                <Text style={styles.footerText}>서비스 안내</Text>
                <Text style={styles.footerText}> | </Text>
                <Text style={styles.footerText}>이용약관</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#FFFFFF',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
    },
    header: {
        alignItems: 'center',
        marginBottom: 50,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#DE5897',
        marginBottom: 5,
    },
    description: {
        fontSize: 16,
        color: '#888888',
        textAlign: 'center',
        lineHeight: 22,
    },
    socialButtonsContainer: {
        width: '100%',
        alignItems: 'center',
        marginBottom: 30,
    },
    socialButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        width: '85%',
        height: 50,
        borderRadius: 8,
        marginBottom: 10,
        borderWidth: 1,
    },
    socialButtonIcon: {
        fontSize: 20,
        marginRight: 10,
    },
    socialButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    separatorContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        width: '85%',
        marginBottom: 20,
    },
    separatorLine: {
        flex: 1,
        height: 1,
        backgroundColor: '#CCCCCC',
    },
    separatorText: {
        marginHorizontal: 10,
        color: '#888888',
        fontSize: 14,
    },
    authButtonsContainer: {
        width: '100%',
        alignItems: 'center',
        marginBottom: 30,
    },
    loginButton: {
        width: '85%',
        height: 50,
        borderRadius: 8,
        marginBottom: 10,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 1,
    },
    loginButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    footer: {
        flexDirection: 'row',
        position: 'absolute',
        bottom: 40,
    },
    footerText: {
        fontSize: 12,
        color: '#888888',
        marginHorizontal: 5,
    },
});
