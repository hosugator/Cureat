import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../context/AuthContext'; // AuthContext 파일 경로로 수정하세요.

const Footer = () => {
    const router = useRouter();
    const { logout } = useAuth(); // useAuth 훅에서 logout 함수를 가져옵니다.


    const handlePress = (path) => {
        router.push(path);
    };

    const handleLogout = () => {
        logout();
    };
    

    return (
        <View style={styles.tabBar}>
            <TouchableOpacity style={styles.tabItemActive} onPress={() => handlePress('/search')}>
                <Text style={styles.tabIconActive}></Text>
                <Text style={styles.tabTextActive}>검색</Text>
            </TouchableOpacity>
            {/* <TouchableOpacity style={styles.tabItemActive} onPress={() => handlePress('/list')}>
                <Text style={styles.tabIconActive}></Text>
                <Text style={styles.tabTextActive}>목록</Text>
            </TouchableOpacity> */}
            <TouchableOpacity style={styles.tabItemActive} onPress={() => handlePress('/home')}>
                <Text style={styles.tabIconActive}></Text>
                <Text style={styles.tabTextActive}>홈</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.tabItem} onPress={() => handlePress('/map')}>
                <Text style={styles.tabIcon}></Text>
                <Text style={styles.tabText}>지도</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.tabItem} onPress={() => handleLogout()}>
                <Text style={styles.tabIcon}></Text>
                <Text style={styles.tabText}>마이</Text>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    tabBar: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
        height: 60,
        borderTopWidth: 1,
        borderTopColor: '#E0E0E0',
        backgroundColor: '#fff',
    },
    tabItem: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
    },
    tabItemActive: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
    },
    tabIcon: {
        fontSize: 24,
        color: '#888',
    },
    tabIconActive: {
        fontSize: 24,
        color: '#888',
    },
    tabText: {
        fontSize: 12,
        color: '#888',
        marginTop: 4,
    },
    tabTextActive: {
        fontSize: 12,
        color: '#888',
        marginTop: 4,
    },
});

export default Footer;
