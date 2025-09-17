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
    const textInputRef = useRef(null);

    const performSearch = async (queryList) => {
        if (!queryList || queryList.length === 0) {
            setSearchResults([]);
            return;
        }

        setIsLoading(true);
        try {
            // 배열을 문자열로 조합해서 API 호출
            const queryString = Array.isArray(queryList) ? queryList.join(' ') : queryList;
            const results = await search(queryString, 1);
            
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
        />
    );
}
