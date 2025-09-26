import React, { useState } from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, ScrollView } from 'react-native';

const UserProfileModal = ({ visible, onClose, onSave, initialProfile = {} }) => {
    const [profile, setProfile] = useState({
        age: initialProfile.age || '',
        gender: initialProfile.gender || '',
        purpose: initialProfile.purpose || '',
        atmosphere: initialProfile.atmosphere || '',
        location: initialProfile.location || ''
    });

    const ageOptions = ['10대', '20대', '30대', '40대', '50대 이상'];
    const genderOptions = ['남성', '여성', '선택안함'];
    const purposeOptions = ['데이트', '가족식사', '회식', '친구모임', '혼밥', '비즈니스'];
    const atmosphereOptions = ['조용한', '힙한', '가성비 좋은', '고급스러운', '캐주얼한', '분위기 좋은'];

    const OptionSection = ({ title, options, selectedValue, onSelect }) => (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>{title}</Text>
            <View style={styles.optionsContainer}>
                {options.map((option) => (
                    <TouchableOpacity
                        key={option}
                        style={[
                            styles.optionButton,
                            selectedValue === option && styles.optionButtonSelected
                        ]}
                        onPress={() => onSelect(option)}
                    >
                        <Text style={[
                            styles.optionText,
                            selectedValue === option && styles.optionTextSelected
                        ]}>
                            {option}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );

    const handleSave = () => {
        onSave(profile);
        onClose();
    };

    return (
        <Modal
            visible={visible}
            animationType="slide"
            transparent={true}
            onRequestClose={onClose}
        >
            <View style={styles.modalOverlay}>
                <View style={styles.modalContent}>
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>검색 조건 설정</Text>
                        <Text style={styles.modalSubtitle}>더 정확한 추천을 위해 정보를 알려주세요</Text>
                        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
                            <Text style={styles.closeButtonText}>×</Text>
                        </TouchableOpacity>
                    </View>

                    <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
                        <OptionSection
                            title="연령대"
                            options={ageOptions}
                            selectedValue={profile.age}
                            onSelect={(value) => setProfile(prev => ({ ...prev, age: value }))}
                        />

                        <OptionSection
                            title="성별"
                            options={genderOptions}
                            selectedValue={profile.gender}
                            onSelect={(value) => setProfile(prev => ({ ...prev, gender: value }))}
                        />

                        <OptionSection
                            title="방문 목적"
                            options={purposeOptions}
                            selectedValue={profile.purpose}
                            onSelect={(value) => setProfile(prev => ({ ...prev, purpose: value }))}
                        />

                        <OptionSection
                            title="원하는 분위기"
                            options={atmosphereOptions}
                            selectedValue={profile.atmosphere}
                            onSelect={(value) => setProfile(prev => ({ ...prev, atmosphere: value }))}
                        />
                    </ScrollView>

                    <View style={styles.modalActions}>
                        <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
                            <Text style={styles.cancelButtonText}>취소</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
                            <Text style={styles.saveButtonText}>적용</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            </View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        justifyContent: 'flex-end',
    },
    modalContent: {
        backgroundColor: '#fff',
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
        maxHeight: '80%',
        paddingBottom: 20,
    },
    modalHeader: {
        padding: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#E0E0E0',
        position: 'relative',
    },
    modalTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333',
        textAlign: 'center',
    },
    modalSubtitle: {
        fontSize: 14,
        color: '#666',
        textAlign: 'center',
        marginTop: 5,
    },
    closeButton: {
        position: 'absolute',
        right: 20,
        top: 15,
        width: 30,
        height: 30,
        justifyContent: 'center',
        alignItems: 'center',
    },
    closeButtonText: {
        fontSize: 24,
        color: '#666',
    },
    scrollContent: {
        paddingHorizontal: 20,
    },
    section: {
        marginVertical: 15,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 10,
    },
    optionsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
    },
    optionButton: {
        paddingHorizontal: 15,
        paddingVertical: 8,
        borderRadius: 20,
        backgroundColor: '#F0F0F0',
        marginBottom: 8,
    },
    optionButtonSelected: {
        backgroundColor: '#DE5897',
    },
    optionText: {
        fontSize: 14,
        color: '#666',
        fontWeight: '500',
    },
    optionTextSelected: {
        color: '#fff',
    },
    modalActions: {
        flexDirection: 'row',
        paddingHorizontal: 20,
        paddingTop: 15,
        gap: 10,
    },
    cancelButton: {
        flex: 1,
        paddingVertical: 12,
        backgroundColor: '#F0F0F0',
        borderRadius: 8,
        alignItems: 'center',
    },
    cancelButtonText: {
        fontSize: 16,
        color: '#666',
        fontWeight: '500',
    },
    saveButton: {
        flex: 1,
        paddingVertical: 12,
        backgroundColor: '#DE5897',
        borderRadius: 8,
        alignItems: 'center',
    },
    saveButtonText: {
        fontSize: 16,
        color: '#fff',
        fontWeight: 'bold',
    },
});

export default UserProfileModal;