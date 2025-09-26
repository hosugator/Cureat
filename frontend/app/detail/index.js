//frontend/app/detail/index.js

import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, Image, ScrollView, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import Footer from '../../components/Footer';

const DetailScreen = () => {
    const router = useRouter();
    const item = useLocalSearchParams();

    // 데이터가 없는 경우를 대비한 기본값 처리
    const restaurant = {
        name: '정보 없음',
        image: 'https://via.placeholder.com/400x200?text=No+Image',
        address: '정보 없음',
        phone: '정보 없음',
        operating_hours: '정보 없음',
        price_range: '정보 없음',
        category: '정보 없음',
        keywords: [],
        pros: [],
        cons: [],
        signature_dishes: [],
        ...item,
        // 배열 필드들은 문자열일 경우 파싱 시도
        keywords: typeof item.keywords === 'string' ? item.keywords.split(',') : item.keywords || [],
        pros: typeof item.pros === 'string' ? item.pros.split(',') : item.pros || [],
        cons: typeof item.cons === 'string' ? item.cons.split(',') : item.cons || [],
        signature_dishes: typeof item.signature_dishes === 'string' ? item.signature_dishes.split(',') : item.signature_dishes || [],
    };

    const handleBack = () => {
        router.back();
    };

    const InfoRow = ({ label, value }) => (
        <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>{label}</Text>
            <Text style={styles.infoValue}>{value || '정보 없음'}</Text>
        </View>
    );

    const TagList = ({ title, tags }) => (
        <View style={styles.tagSection}>
            <Text style={styles.sectionTitle}>{title}</Text>
            <View style={styles.tagContainer}>
                {tags && tags.length > 0 ? (
                    tags.map((tag, index) => (
                        <View key={index} style={styles.tag}>
                            <Text style={styles.tagText}>{tag}</Text>
                        </View>
                    ))
                ) : (
                    <Text style={styles.infoValue}>정보 없음</Text>
                )}
            </View>
        </View>
    );

    return (
        <SafeAreaView style={styles.safeArea}>
            <View style={styles.header}>
                <TouchableOpacity onPress={handleBack} style={styles.backButton}>
                    <Text style={styles.backIcon}>←</Text>
                </TouchableOpacity>
                <Text style={styles.headerTitle} numberOfLines={1}>{restaurant.name}</Text>
            </View>

            <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
                <Image source={{ uri: restaurant.image }} style={styles.mainImage} />
                
                <View style={styles.card}>
                    <Text style={styles.title}>{restaurant.name}</Text>
                    
                    <View style={styles.infoBox}>
                        <InfoRow label="📍 주소" value={restaurant.address} />
                        <InfoRow label="📞 전화번호" value={restaurant.phone} />
                        <InfoRow label="⏰ 운영시간" value={restaurant.operating_hours} />
                        <InfoRow label="💰 가격대" value={restaurant.price_range} />
                        <InfoRow label="🍽️ 카테고리" value={restaurant.category} />
                    </View>

                    <TagList title="대표 메뉴" tags={restaurant.signature_dishes} />
                    <TagList title="👍 장점" tags={restaurant.pros} />
                    <TagList title="👎 단점" tags={restaurant.cons} />
                    <TagList title="✨ 키워드" tags={restaurant.keywords} />
                </View>
            </ScrollView>

            <Footer />
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: '#F4F4F4',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 15,
        backgroundColor: '#FFFFFF',
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    backButton: {
        position: 'absolute',
        left: 15,
        padding: 5,
        zIndex: 1,
    },
    backIcon: {
        fontSize: 24,
        color: '#000',
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#DE5897',
        textAlign: 'center',
        marginHorizontal: 50,
    },
    container: {
        flex: 1,
    },
    contentContainer: {
        paddingBottom: 100, // Footer height
    },
    mainImage: {
        width: '100%',
        height: 250,
    },
    card: {
        backgroundColor: '#FFFFFF',
        margin: 15,
        borderRadius: 10,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 5,
        elevation: 3,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        color: '#333',
    },
    infoBox: {
        marginBottom: 20,
    },
    infoRow: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        marginBottom: 12,
    },
    infoLabel: {
        fontSize: 16,
        color: '#333',
        fontWeight: '600',
        width: 90,
    },
    infoValue: {
        fontSize: 16,
        color: '#555',
        flex: 1,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 10,
        borderTopColor: '#EEE',
        borderTopWidth: 1,
        paddingTop: 20,
    },
    tagSection: {
        marginBottom: 10,
    },
    tagContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    tag: {
        backgroundColor: '#EFEFEF',
        borderRadius: 15,
        paddingVertical: 6,
        paddingHorizontal: 12,
        marginRight: 10,
        marginBottom: 10,
    },
    tagText: {
        fontSize: 14,
        color: '#555',
    },
});

export default DetailScreen;
