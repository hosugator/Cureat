import React, { useState, useEffect, useRef } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { search } from '../../services/searchService';
import ResultScreen from '../../components/ResultScreen';

export default function SearchResultsScreen() {
    const { initialQuery } = useLocalSearchParams();
    const router = useRouter();

    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilters, setActiveFilters] = useState([]);
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [userProfile, setUserProfile] = useState({
        // 로그인한 사용자의 DB 프로필 데이터가 로드될 예정
        // 현재는 빈 객체로 시작
    });
    const textInputRef = useRef(null);

    const performSearch = async (queryList) => {
        if (!queryList || queryList.length === 0) {
            setSearchResults([]);
            return;
        }

        setIsLoading(true);
        try {
            // 배열을 문자열로 조합하여 자연어 쿼리 생성
            const queryString = Array.isArray(queryList) ? queryList.join(' ') : queryList;
            
            // TODO: 실제 로그인한 사용자 ID 가져오기 (AuthContext에서)
            // 현재는 테스트용으로 user_id = 1 사용
            const userId = 1; // 추후 AuthContext에서 실제 사용자 ID 가져올 예정
            
            const results = await search(queryString, userId);
            
            // API 응답 구조에 맞게 결과 처리
            if (results && results.restaurants) {
                setSearchResults(results.restaurants);
            } else {
                setSearchResults([]);
            }
        } catch (error) {
            console.error('Search error:', error);
            setSearchResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (initialQuery) {
            const initialFilter = { id: Date.now(), text: initialQuery, active: true };
            setActiveFilters([initialFilter]);
            performSearch([initialQuery]);
        }
    }, [initialQuery]);

    const handleSearch = () => {
        if (searchQuery.trim()) {
            const newFilter = { id: Date.now(), text: searchQuery.trim(), active: true };
            const newFilters = [...activeFilters, newFilter];
            setActiveFilters(newFilters);
            setSearchQuery('');
            performSearch(newFilters.filter(f => f.active).map(f => f.text));
        }
    };

    const handleBack = () => {
        router.back();
    };

    const toggleFilter = (id) => {
        const updatedFilters = activeFilters.map(filter =>
            filter.id === id ? { ...filter, active: !filter.active } : filter
        );
        setActiveFilters(updatedFilters);
        performSearch(updatedFilters.filter(f => f.active).map(f => f.text));
    };

    const updateUserProfile = (newProfile) => {
        setUserProfile(newProfile);
        // 프로필이 변경되면 현재 활성 필터로 다시 검색
        const activeQueries = activeFilters.filter(f => f.active).map(f => f.text);
        if (activeQueries.length > 0) {
            performSearch(activeQueries);
        }
    };

    return (
        <ResultScreen
            searchResults={searchResults}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            handleSearch={handleSearch}
            handleBack={handleBack}
            isLoading={isLoading}
            activeFilters={activeFilters}
            toggleFilter={toggleFilter}
            textInputRef={textInputRef}
            userProfile={userProfile}
            updateUserProfile={updateUserProfile}
        />
    );
}
