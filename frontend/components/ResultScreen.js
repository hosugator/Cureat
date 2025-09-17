import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, FlatList, Image, TextInput, Keyboard, PanResponder } from 'react-native';
import { useNavigation, useRouter } from 'expo-router';
import Footer from './Footer';

const ResultCard = ({ item, onPress }) => (
    <TouchableOpacity onPress={() => onPress(item)} style={styles.card}>
        <Image source={{ uri: item.image }} style={styles.cardImage} />
        <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>{item.name}</Text>
            <View style={styles.cardRatingContainer}>
                <Text style={styles.cardRating}>★ {item.rating}</Text>
                <Text style={styles.cardReviews}>({item.reviews})</Text>
            </View>
            <Text style={styles.cardDescription}>{item.description}</Text>
        </View>
    </TouchableOpacity>
);

const ResultScreen = ({
    searchResults,
    searchQuery,
    setSearchQuery,
    handleSearch,
    handleBack,
    isLoading,
    activeFilters,
    toggleFilter,
    textInputRef
}) => {
    const navigation = useNavigation();
    const router = useRouter();
    const [keyboardHeight, setKeyboardHeight] = useState(0);
    const footerHeight = 100; // Footer 컴포넌트의 높이 (스타일시트에서 설정된 값)

    useEffect(() => {
        const keyboardDidShowListener = Keyboard.addListener(
            'keyboardDidShow',
            (e) => {
                setKeyboardHeight(e.endCoordinates.height);
            }
        );
        const keyboardDidHideListener = Keyboard.addListener(
            'keyboardDidHide',
            () => {
                setKeyboardHeight(0);
            }
        );

        return () => {
            keyboardDidShowListener.remove();
            keyboardDidHideListener.remove();
        };
    }, []);

    const navigateToDetail = (item) => {
        router.push({ pathname: 'detail', params: item });
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <View style={styles.header}>
                <TouchableOpacity onPress={handleBack} style={styles.backButton}>
                    <Text style={styles.backIcon}>←</Text>
                </TouchableOpacity>
                <Text style={styles.headerTitle}>Cureat</Text>
            </View>
            <View style={styles.filterTagContainer}>
                {activeFilters.map(filter => (
                    <TouchableOpacity
                        key={filter.id}
                        onPress={() => toggleFilter(filter.id)}
                        style={[
                            styles.filterTag,
                            filter.active ? styles.filterTagActive : styles.filterTagInactive
                        ]}
                    >
                        <Text style={[
                            styles.filterTagText,
                            filter.active ? styles.filterTagTextActive : styles.filterTagTextInactive
                        ]}>
                            {filter.text}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
            <FlatList
                data={searchResults}
                renderItem={({ item }) => <ResultCard item={item} onPress={navigateToDetail} />}
                keyExtractor={item => item.id}
                ListEmptyComponent={
                    isLoading ? (
                        <Text style={styles.loadingText}>검색 중...</Text>
                    ) : (
                        <Text style={styles.noResultsText}>
                            {activeFilters.length > 0 ? '선택된 필터에 해당하는 결과가 없습니다.' : '검색어를 입력해주세요.'}
                        </Text>
                    )
                }
                style={styles.resultsList}
                contentContainerStyle={[
                    styles.resultsListContent,
                    // 검색창과 푸터 높이만큼 패딩을 추가
                    { paddingBottom: 60 + (styles.footerSearchContainer.paddingVertical * 2) + styles.searchBarWrapper.height }
                ]}
            />
            {/* 키보드가 나타나면 bottom 값을 동적으로 변경 */}
            <View style={[
                styles.footerSearchContainer,
                { bottom: keyboardHeight > 0 ? keyboardHeight : footerHeight }
            ]}>
                <View style={styles.searchBarWrapper}>
                    <TextInput
                        ref={textInputRef}
                        style={styles.searchInput}
                        placeholder="음식점, 요리 또는 지역을 검색하세요"
                        placeholderTextColor="#888"
                        value={searchQuery}
                        onChangeText={setSearchQuery}
                        onSubmitEditing={handleSearch}
                    />
                </View>
            </View>
            <Footer />
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: '#FFFFFF',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 15,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
    },
    backButton: {
        position: 'absolute',
        left: 15,
        padding: 5,
    },
    backIcon: {
        fontSize: 24,
        color: '#000',
    },
    headerTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#DE5897',
    },
    filterTagContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        paddingHorizontal: 15,
        paddingVertical: 10,
        borderBottomWidth: 0,
        borderBottomColor: '#E0E0E0',
    },
    filterTag: {
        borderRadius: 20,
        paddingVertical: 8,
        paddingHorizontal: 15,
        marginRight: 10,
        marginBottom: 10,
    },
    filterTagActive: {
        backgroundColor: '#DE5897',
    },
    filterTagInactive: {
        backgroundColor: '#E0E0E0',
    },
    filterTagText: {
        fontSize: 14,
        fontWeight: 'bold',
    },
    filterTagTextActive: {
        color: '#fff',
    },
    filterTagTextInactive: {
        color: '#666',
    },
    resultsList: {
        flex: 1,
        paddingHorizontal: 15,
    },
    resultsListContent: {
        paddingTop: 10,
        paddingBottom: 20,
    },
    loadingText: {
        textAlign: 'center',
        marginTop: 50,
        fontSize: 16,
        color: '#888',
    },
    noResultsText: {
        textAlign: 'center',
        marginTop: 50,
        fontSize: 16,
        color: '#888',
    },
    card: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F9F9F9',
        borderRadius: 10,
        padding: 10,
        marginBottom: 15,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 5,
        elevation: 3,
    },
    cardImage: {
        width: 80,
        height: 80,
        borderRadius: 8,
        marginRight: 15,
    },
    cardContent: {
        flex: 1,
    },
    cardTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#000',
    },
    cardRatingContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginVertical: 4,
    },
    cardRating: {
        fontSize: 14,
        color: '#F4B400',
        fontWeight: 'bold',
        marginRight: 5,
    },
    cardReviews: {
        fontSize: 12,
        color: '#888',
    },
    cardDescription: {
        fontSize: 13,
        color: '#666',
    },
    footerSearchContainer: {
        position: 'absolute',
        left: 0,
        right: 0,
        backgroundColor: '#fff',
        paddingHorizontal: 20,
        paddingVertical: 10,
        borderTopWidth: 0,
        borderTopColor: '#E0E0E0',
        zIndex: 10,
    },
    searchBarWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F5F5F5',
        borderRadius: 25,
        height: 45,
        paddingLeft: 10,
    },
    searchInput: {
        flex: 1,
        height: '100%',
        paddingHorizontal: 15,
        fontSize: 16,
        color: '#000',
    },
});

export default ResultScreen;