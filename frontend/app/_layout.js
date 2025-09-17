import React, { useEffect, useState } from 'react';
import { Stack, useRouter, SplashScreen } from 'expo-router';
import { AuthProvider, useAuth } from '../context/AuthContext';

// AuthProvider가 앱의 상태를 로드할 때까지 Splash Screen을 보여줍니다.
SplashScreen.preventAutoHideAsync();

const AppContent = () => {
    const router = useRouter();
    const { isLoggedIn } = useAuth();
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        // isReady가 false일 때만 실행
        if (!isReady) {
            if (isLoggedIn !== null) {
                setIsReady(true);
                SplashScreen.hideAsync();
            }
        }
    }, [isLoggedIn, isReady]);

    useEffect(() => {
        // isReady가 true가 되고 isLoggedIn이 변경될 때만 실행
        if (isReady) {
            if (isLoggedIn) {
                router.replace('/home');
            } else {
                router.replace('/');
            }
        }
    }, [isReady, isLoggedIn, router]);

    // isReady 상태에 따라 화면을 보여줍니다.
    if (!isReady) {
        return null;
    }

    return (
        <Stack>
            <Stack.Screen name="index" options={{ headerShown: false }} />
            <Stack.Screen name="login/index" options={{ headerShown: false }} />
            <Stack.Screen name="home/index" options={{ headerShown: false }} />
            <Stack.Screen name="search/index" options={{ headerShown: false }} />
            <Stack.Screen name="detail/index" options={{ headerShown: false }} />


        </Stack>
    );
};

export default function RootLayout() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}
