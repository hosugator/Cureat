import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TextInput, TouchableOpacity, FlatList, Image, Alert } from 'react-native';
import Footer from './Footer';

// 더 안정적인 이미지 URL로 교체된 데이터
const popularRestaurants = [
  { id: '1', name: 'The Cozy Corner', rating: 4.5, reviews: '1200+', image: 'https://upload.wikimedia.org/wikipedia/commons/4/45/A_small_cup_of_coffee.JPG' },
  { id: '2', name: 'The Urban Grill', rating: 4.2, reviews: '800+', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cooking_yakitori.jpg/1024px-Cooking_yakitori.jpg' },
  { id: '3', name: 'Italian Delight', rating: 4.8, reviews: '2500+', image: 'https://upload.wikimedia.org/wikipedia/commons/4/4d/Tagliatelle_al_rag%C3%B9_%28image_modified%29.jpg' },
  { id: '4', name: 'Seafood Heaven', rating: 4.1, reviews: '500+', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/%E8%8C%B9%E3%81%A7%E3%82%AC%E3%83%8B.jpg/2560px-%E8%8C%B9%E3%81%A7%E3%82%AC%E3%83%8B.jpg' },
];

const personalizedRecommendations = [
  { id: '1', name: 'Cozy Brunch Spot', rating: 4.6, reviews: '950+', image: 'https://cdn.apartmenttherapy.info/image/upload/f_auto,q_auto:eco,c_fit,w_730,h_487/k%2FFood%20Fest%202021%2FBrunch%20Fest%2FPhoto%2F2021-03-30_ATK-47735-no-whip_no-yolk-break_3-2' },
  { id: '2', name: 'Late Night Tacos', rating: 4.3, reviews: '620+', image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg/500px-001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg' },
  { id: '3', name: 'Healthy Bistro', rating: 4.7, reviews: '1800+', image: 'https://healthy-bistro.com/wp-content/uploads/2025/05/HealthyChickenSandwich.jpg' },
  { id: '4', name: 'Authentic Thai', rating: 4.4, reviews: '1100+', image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJzW0uBbXAYb4L7x0dJzwPHLdXKru76_Xi2Q&s' },
];

const filterCategories = [
  { id: 'weather', name: '날씨', tags: ['비 오는 날', '더운 날', '추운 날'] },
  { id: 'cuisine', name: '카테고리', tags: ['한식', '양식', '일식', '중식', '아시아'] },
  { id: 'type', name: '음식 종류', tags: ['육류', '해산물', '채식', '샐러드'] },
];

const RestaurantCard = ({ item }) => (
  <View style={styles.card}>
    <Image source={{ uri: item.image }} style={styles.cardImage} />
    <Text style={styles.cardTitle}>{item.name}</Text>
    <View style={styles.cardRatingContainer}>
      <Text style={styles.cardRating}>★ {item.rating}</Text>
      <Text style={styles.cardReviews}>({item.reviews})</Text>
    </View>
  </View>
);

const HomeUI = ({ handleLogout, handleSearch }) => {
  const [isCourseActive, setIsCourseActive] = useState(false);
  const [openFilter, setOpenFilter] = useState(null);
  const [selectedFilters, setSelectedFilters] = useState({});
  const [searchQuery, setSearchQuery] = useState(''); // 검색어 상태 추가

  const handleFilterPress = (filterId) => {
    setOpenFilter(openFilter === filterId ? null : filterId);
  };

  const handleTagSelect = (filterId, tagName) => {
    setSelectedFilters(prevFilters => ({
      ...prevFilters,
      [filterId]: tagName
    }));
    setOpenFilter(null);
  };

  const handleResetFilters = () => {
    setSelectedFilters({});
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>Cureat</Text>
          {/* <TouchableOpacity onPress={() => console.log('Menu')}>
            <Text style={styles.menuIcon}>☰</Text>
          </TouchableOpacity> */}
        </View>

        {/* Search Bar & Categories */}
        <View style={styles.searchContainer}>
          <View style={styles.searchBarWrapper}>
            {/* <TouchableOpacity
              style={isCourseActive ? styles.searchButtonActive : styles.searchButtonInactive}
              onPress={() => setIsCourseActive(!isCourseActive)}
            >
              <Text style={isCourseActive ? styles.searchButtonTextActive : styles.searchButtonTextInactive}>
                코스
              </Text>
            </TouchableOpacity> */}
            <TextInput
              style={styles.searchInput}
              placeholder="음식점, 요리 또는 지역을 검색하세요"
              placeholderTextColor="#888"
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={() => handleSearch(searchQuery)} // 엔터 키 입력 시 검색 실행
            />
          </View>
          <View style={styles.tagContainer}>
            <TouchableOpacity onPress={handleResetFilters} style={styles.resetButton}>
              <Text style={styles.resetButtonText}>↻</Text>
            </TouchableOpacity>
            {filterCategories.map(filter => (
              <View key={filter.id} style={styles.filterTagWrapper}>
                <TouchableOpacity onPress={() => handleFilterPress(filter.id)}
                  style={[
                    styles.filterTag,
                    !selectedFilters[filter.id] && styles.filterTagInactive // 선택되지 않았을 때 스타일 적용
                  ]}
                >
                  <Text style={[
                    styles.filterTagText,
                    !selectedFilters[filter.id] && styles.filterTagTextInactive // 선택되지 않았을 때 텍스트 스타일 적용
                  ]}>
                    {selectedFilters[filter.id] || filter.name}
                  </Text>
                </TouchableOpacity>
                {openFilter === filter.id && (
                  <View style={styles.filterDropdown}>
                    <TouchableOpacity
                      key="none"
                      style={styles.dropdownItem}
                      onPress={() => handleTagSelect(filter.id, null)} // '선택 안 함' 기능
                    >
                      <Text style={styles.dropdownItemText}>선택 안 함</Text>
                    </TouchableOpacity>
                    {filter.tags.map(tag => (
                      <TouchableOpacity
                        key={tag}
                        style={styles.dropdownItem}
                        onPress={() => handleTagSelect(filter.id, tag)}
                      >
                        <Text style={styles.dropdownItemText}>{tag}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                )}
              </View>
            ))}
          </View>
        </View>

        {/* Popular Restaurants */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Popular Now</Text>
            <View style={styles.arrows}>
              <TouchableOpacity><Text style={styles.arrow}>{'<'}</Text></TouchableOpacity>
              <TouchableOpacity><Text style={styles.arrow}>{'>'}</Text></TouchableOpacity>
            </View>
          </View>
          <FlatList
            horizontal
            showsHorizontalScrollIndicator={false}
            data={popularRestaurants}
            renderItem={({ item }) => <RestaurantCard item={item} />}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.flatListContainer}
          />
        </View>

        {/* Personalized Recommendations */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>For You</Text>
            <View style={styles.arrows}>
              <TouchableOpacity><Text style={styles.arrow}>{'<'}</Text></TouchableOpacity>
              <TouchableOpacity><Text style={styles.arrow}>{'>'}</Text></TouchableOpacity>
            </View>
          </View>
          <FlatList
            horizontal
            showsHorizontalScrollIndicator={false}
            data={personalizedRecommendations}
            renderItem={({ item }) => <RestaurantCard item={item} />}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.flatListContainer}
          />
        </View>
      </ScrollView>

      {/* Footer / Tab Bar */}
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
    paddingHorizontal: 15,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingBottom: 20,
  },
  logo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#DE5897', // 로고 색상 변경
  },
  menuIcon: {
    fontSize: 24,
    color: '#000',
  },
  searchContainer: {
    marginBottom: 20,
  },
  searchBarWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 25,
    height: 45,
    paddingLeft: 10,
    marginBottom: 15,
  },
  searchButtonActive: {
    backgroundColor: '#DE5897',
    paddingVertical: 5,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  searchButtonInactive: {
    backgroundColor: '#fff',
    borderColor: '#E0E0E0',
    borderWidth: 1,
    paddingVertical: 5,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  searchButtonTextActive: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  searchButtonTextInactive: {
    color: '#888',
    fontWeight: 'bold',
    fontSize: 14,
  },
  searchInput: {
    flex: 1,
    height: '100%',
    paddingHorizontal: 15,
    fontSize: 16,
    color: '#000',
  },
  tagContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    flexWrap: 'wrap',
  },
  resetButton: {
    // backgroundColor: '#E0E0E0',
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 15,
    marginRight: 0,
    marginBottom: 0,
  },
  resetButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: 'bold',
  },
  filterTagWrapper: {
    position: 'relative',
    marginRight: 10,
    marginBottom: 10,
  },
  filterTag: {
    backgroundColor: '#F7E7E7',
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 15,
  },
  filterTagInactive: {
    backgroundColor: '#E0E0E0',
  },
  filterTagText: {
    color: '#DE5897',
    fontSize: 14,
  },
  filterTagTextInactive: {
    color: '#666',
  },
  filterDropdown: {
    position: 'absolute',
    top: '100%',
    left: 0,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 5,
    padding: 10,
    zIndex: 10,
    minWidth: 150,
  },
  dropdownItem: {
    paddingVertical: 8,
    paddingHorizontal: 5,
  },
  dropdownItemText: {
    fontSize: 14,
    color: '#000',
  },
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
  },
  arrows: {
    flexDirection: 'row',
  },
  arrow: {
    fontSize: 20,
    color: '#888',
    marginHorizontal: 5,
  },
  flatListContainer: {
    paddingVertical: 10,
  },
  card: {
    width: 150,
    marginRight: 15,
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  cardImage: {
    width: '100%',
    height: 150,
  },
  cardTitle: {
    fontWeight: 'bold',
    marginTop: 8,
    marginLeft: 8,
  },
  cardRatingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
    marginBottom: 8,
    marginLeft: 8,
  },
  cardRating: {
    fontSize: 12,
    color: '#DE5897',
    fontWeight: 'bold',
    marginRight: 5,
  },
  cardReviews: {
    fontSize: 12,
    color: '#888',
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
    alignItems: 'center',
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 5,
  },
  tabText: {
    fontSize: 12,
    color: '#888',
  },
  tabItemActive: {
    alignItems: 'center',
    borderTopWidth: 2,
    borderTopColor: '#DE5897',
    paddingTop: 5,
  },
  tabIconActive: {
    fontSize: 20,
    marginBottom: 5,
    color: '#DE5897',
  },
  tabTextActive: {
    fontSize: 12,
    color: '#DE5897',
    fontWeight: 'bold',
  },
});

export default HomeUI;