import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, Image, TouchableOpacity, ScrollView, Modal, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import Footer from './Footer';

// 임시 리스트 데이터 (실제로는 서버에서 가져와야 함)
const dummyLists = [
    { id: '1', name: '가고 싶은 곳' },
    { id: '2', name: '친구 추천 맛집' },
    { id: '3', name: '데이트 코스' },
];

const DetailScreen = ({ data, onBack }) => {
    const router = useRouter();
    const [modalVisible, setModalVisible] = useState(false);

    const handleAddToList = () => {
        setModalVisible(true);
    };

    const handleMapAdd = () => {
        Alert.alert(
            "지도에 추가",
            `${data.name}을(를) 지도에 목적지로 추가합니다.`
        );
        // TODO: 지도 페이지로 이동하는 로직 구현
        // router.push({ pathname: 'map', params: { destination: data.name } });
    };

    const handleListSelect = (listName) => {
        Alert.alert(
            "리스트에 추가",
            `${data.name}이(가) "${listName}" 리스트에 추가되었습니다.`
        );
        setModalVisible(false);
    };

    const handleBack = () => {
        router.back();
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <ScrollView style={styles.container}>
                <Image source={{ uri: data.image }} style={styles.headerImage} />
                <TouchableOpacity onPress={handleBack} style={styles.backButton}>
                    <Text style={styles.backIcon}>←</Text>
                </TouchableOpacity>
                <View style={styles.contentContainer}>
                    <Text style={styles.name}>{data.name}</Text>
                    <View style={styles.ratingContainer}>
                        <Text style={styles.rating}>★ {data.rating}</Text>
                        <Text style={styles.reviews}>({data.reviews})</Text>
                    </View>
                    <View style={styles.buttonContainer}>
                        <TouchableOpacity style={styles.addButton} onPress={handleAddToList}>
                            <Text style={styles.addButtonText}>담기</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.mapButton} onPress={handleMapAdd}>
                            <Text style={styles.mapButtonText}>지도에 추가</Text>
                        </TouchableOpacity>
                    </View>
                    <View style={styles.infoSection}>
                        <Text style={styles.sectionTitle}>상세 정보</Text>
                        <Text style={styles.infoText}>주소: {data.address}</Text>
                        <Text style={styles.infoText}>운영 시간: {data.hours}</Text>
                        <Text style={styles.infoText}>전화번호: {data.phone}</Text>
                    </View>
                    <View style={styles.descriptionSection}>
                        <Text style={styles.sectionTitle}>설명</Text>
                        <Text style={styles.descriptionText}>{data.description}</Text>
                    </View>
                    <View style={styles.tagsContainer}>
                        {data.tags.map((tag, index) => (
                            <View key={index} style={styles.tag}>
                                <Text style={styles.tagText}>{tag}</Text>
                            </View>
                        ))}
                    </View>
                </View>
            </ScrollView>

            <Modal
                animationType="slide"
                transparent={true}
                visible={modalVisible}
                onRequestClose={() => setModalVisible(false)}
            >
                <View style={styles.modalOverlay}>
                    <View style={styles.modalContent}>
                        <Text style={styles.modalTitle}>리스트 선택</Text>
                        {dummyLists.map(list => (
                            <TouchableOpacity
                                key={list.id}
                                style={styles.listButton}
                                onPress={() => handleListSelect(list.name)}
                            >
                                <Text style={styles.listButtonText}>{list.name}</Text>
                            </TouchableOpacity>
                        ))}
                        <TouchableOpacity style={styles.modalCloseButton} onPress={() => setModalVisible(false)}>
                            <Text style={styles.modalCloseText}>닫기</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </Modal>

            <Footer />
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: '#FFFFFF',
    },
    container: {
        flex: 1,
    },
    headerImage: {
        width: '100%',
        height: 250,
        resizeMode: 'cover',
    },
    backButton: {
        position: 'absolute',
        top: 20,
        left: 20,
        padding: 10,
        backgroundColor: 'rgba(0,0,0,0.5)',
        borderRadius: 25,
    },
    backIcon: {
        fontSize: 24,
        color: '#fff',
    },
    contentContainer: {
        padding: 20,
        marginTop: -50,
        backgroundColor: '#fff',
        borderTopLeftRadius: 30,
        borderTopRightRadius: 30,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -5 },
        shadowOpacity: 0.1,
        shadowRadius: 10,
        elevation: 10,
    },
    name: {
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 5,
        color: '#000',
    },
    ratingContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 20,
    },
    rating: {
        fontSize: 18,
        color: '#F4B400',
        fontWeight: 'bold',
        marginRight: 5,
    },
    reviews: {
        fontSize: 16,
        color: '#888',
    },
    buttonContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 20,
    },
    addButton: {
        flex: 1,
        marginRight: 10,
        backgroundColor: '#DE5897',
        borderRadius: 25,
        paddingVertical: 12,
        alignItems: 'center',
    },
    addButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
    mapButton: {
        flex: 1,
        marginLeft: 10,
        backgroundColor: '#4CAF50',
        borderRadius: 25,
        paddingVertical: 12,
        alignItems: 'center',
    },
    mapButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
    infoSection: {
        marginBottom: 20,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 10,
        color: '#000',
    },
    infoText: {
        fontSize: 16,
        color: '#666',
        marginBottom: 5,
    },
    descriptionSection: {
        marginBottom: 20,
    },
    descriptionText: {
        fontSize: 16,
        lineHeight: 24,
        color: '#666',
    },
    tagsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 20,
    },
    tag: {
        backgroundColor: '#E0E0E0',
        borderRadius: 15,
        paddingVertical: 5,
        paddingHorizontal: 10,
        marginRight: 10,
        marginBottom: 10,
    },
    tagText: {
        fontSize: 14,
        color: '#666',
    },
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
        color: '#DE5897',
    },
    tabText: {
        fontSize: 12,
        color: '#888',
        marginTop: 4,
    },
    tabTextActive: {
        fontSize: 12,
        color: '#DE5897',
        marginTop: 4,
        fontWeight: 'bold',
    },
    modalOverlay: {
        flex: 1,
        justifyContent: 'flex-end',
        backgroundColor: 'rgba(0,0,0,0.5)',
    },
    modalContent: {
        backgroundColor: '#fff',
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
        padding: 20,
        alignItems: 'center',
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 20,
        color: '#000',
    },
    listButton: {
        width: '100%',
        padding: 15,
        alignItems: 'center',
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    listButtonText: {
        fontSize: 18,
        color: '#000',
    },
    modalCloseButton: {
        marginTop: 20,
        padding: 15,
        backgroundColor: '#DE5897',
        borderRadius: 25,
        width: '80%',
        alignItems: 'center',
    },
    modalCloseText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default DetailScreen;
