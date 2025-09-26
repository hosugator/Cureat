import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { signUp } from '../../services/userService'; // 방금 만든 서비스 임포트

// 아이콘 임포트 (lucide-react-native 사용 가정)
// import { ArrowLeft, ChevronDown } from 'lucide-react-native';

// 임시 아이콘 컴포넌트
const ArrowLeft = () => <Text style={{fontSize: 24}}>{'<'}</Text>;
const ChevronDown = () => <Text>{'▼'}</Text>;

export default function SignUpScreen() {
  const router = useRouter();
  const [signUpForm, setSignUpForm] = useState({
    email: '',
    password: '',
    passwordConfirm: '',
    name: '',
    birthdate: '', // 생년월일 필드 추가
    gender: '',
    phone: '',
    address: '',
    interests: '',
    allergies: false,
    allergies_detail: '',
  });

  const handleSignUpChange = (name, value) => {
    setSignUpForm((prev) => ({ ...prev, [name]: value }));
  };

  const getFieldName = (field) => {
    const fieldNames = {
      name: '이름',
      email: '이메일',
      password: '비밀번호',
      birthdate: '생년월일',
      gender: '성별',
      phone: '전화번호',
      address: '주소'
    };
    return fieldNames[field] || field;
  };

  const handleBirthdateChange = (value) => {
    // 숫자만 입력 허용
    const numericValue = value.replace(/[^0-9]/g, '');
    if (numericValue.length <= 8) {
      handleSignUpChange('birthdate', numericValue);
    }
  };

  const formatBirthdateDisplay = (birthdate) => {
    if (birthdate.length === 8) {
      const year = birthdate.substring(0, 4);
      const month = birthdate.substring(4, 6);
      const day = birthdate.substring(6, 8);
      return `${year}년 ${month}월 ${day}일`;
    }
    return birthdate;
  };

  const formatBirthdateForAPI = (birthdate) => {
    if (birthdate.length === 8) {
      const year = birthdate.substring(0, 4);
      const month = birthdate.substring(4, 6);
      const day = birthdate.substring(6, 8);
      return `${year}-${month}-${day}`;
    }
    return birthdate;
  };

  const handleSignUpSubmit = async () => {
    // 기본 유효성 검사
    if (signUpForm.password !== signUpForm.passwordConfirm) {
      Alert.alert('오류', '비밀번호가 일치하지 않습니다.');
      return;
    }

    // 필수 필드 검사
    const requiredFields = ['name', 'email', 'password', 'birthdate', 'gender', 'phone', 'address'];
    for (const field of requiredFields) {
      if (!signUpForm[field] || signUpForm[field].trim() === '') {
        Alert.alert('오류', `${getFieldName(field)}을(를) 입력해주세요.`);
        return;
      }
    }

    try {
        // 생년월일 유효성 검사
        if (signUpForm.birthdate.length !== 8) {
          Alert.alert('오류', '생년월일을 8자리 숫자로 입력해주세요. (예: 19951024)');
          return;
        }

        // 백엔드 스키마에 맞게 데이터 변환
        const payload = {
            name: signUpForm.name.trim(),
            email: signUpForm.email.trim(),
            password: signUpForm.password,
            birthdate: formatBirthdateForAPI(signUpForm.birthdate), // YYYYMMDD -> YYYY-MM-DD 변환
            gender: signUpForm.gender,
            phone: signUpForm.phone.replace(/-/g, ''), // 하이픈 제거
            address: signUpForm.address.trim(),
            interests: signUpForm.interests.trim() || null,
            allergies: signUpForm.allergies,
            allergies_detail: signUpForm.allergies && signUpForm.allergies_detail.trim() 
              ? signUpForm.allergies_detail.trim() 
              : null
        };

        console.log('회원가입 요청 데이터:', payload); // 디버깅용 로그
      
      await signUp(payload);
      Alert.alert('성공', '회원가입이 완료되었습니다. 로그인해주세요.', [
        { text: '확인', onPress: () => router.push('/login') },
      ]);
    } catch (error) {
      console.error(error);
      Alert.alert('회원가입 실패', error.message || '오류가 발생했습니다.');
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <ArrowLeft />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Cureat</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView 
        style={styles.formContainer}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={styles.scrollContentContainer}
      >
        {/* 이메일 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>이메일 (아이디)</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.email}
                onChangeText={(value) => handleSignUpChange('email', value)}
                placeholder="이메일 주소를 입력해주세요"
                keyboardType="email-address"
                autoCapitalize="none"
            />
        </View>

        {/* 비밀번호 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>비밀번호 (영문 + 숫자 8~20자)</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.password}
                onChangeText={(value) => handleSignUpChange('password', value)}
                placeholder="비밀번호를 입력해주세요"
                secureTextEntry
            />
        </View>

        {/* 비밀번호 재확인 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>비밀번호 재확인</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.passwordConfirm}
                onChangeText={(value) => handleSignUpChange('passwordConfirm', value)}
                placeholder="비밀번호를 다시 입력해주세요"
                secureTextEntry
            />
            {signUpForm.password && signUpForm.passwordConfirm && signUpForm.password !== signUpForm.passwordConfirm && (
                <Text style={styles.errorText}>비밀번호가 일치하지 않습니다.</Text>
            )}
        </View>

        {/* 이름 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>이름</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.name}
                onChangeText={(value) => handleSignUpChange('name', value)}
                placeholder="이름을 입력해주세요"
            />
        </View>

        {/* 생년월일 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>생년월일</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.birthdate}
                onChangeText={(value) => handleBirthdateChange(value)}
                placeholder="예: 19951024 (8자리 숫자)"
                keyboardType="numeric"
                maxLength={8}
            />
            {signUpForm.birthdate && signUpForm.birthdate.length === 8 && (
                <Text style={styles.helperText}>
                    입력된 날짜: {formatBirthdateDisplay(signUpForm.birthdate)}
                </Text>
            )}
        </View>

        {/* 성별 */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>성별</Text>
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[styles.button, signUpForm.gender === '남자' && styles.buttonActive]}
              onPress={() => handleSignUpChange('gender', '남자')}
            >
              <Text style={[styles.buttonText, signUpForm.gender === '남자' && styles.buttonTextActive]}>남자</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, signUpForm.gender === '여자' && styles.buttonActive]}
              onPress={() => handleSignUpChange('gender', '여자')}
            >
              <Text style={[styles.buttonText, signUpForm.gender === '여자' && styles.buttonTextActive]}>여자</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 전화번호 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>전화번호</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.phone}
                onChangeText={(value) => handleSignUpChange('phone', value.replace(/[^0-9]/g, ''))}
                placeholder="01012345678 (11자리)"
                keyboardType="numeric"
                maxLength={11}
            />
        </View>
        
        {/* 주소 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>주소</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.address}
                onChangeText={(value) => handleSignUpChange('address', value)}
                placeholder="주소를 입력해주세요"
            />
        </View>
        
        {/* 관심사 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>관심사</Text>
            <TextInput
                style={styles.input}
                value={signUpForm.interests}
                onChangeText={(value) => handleSignUpChange('interests', value)}
                placeholder="예: 일식, 양식, 파스타, 미슐랭"
            />
        </View>

        {/* 알러지 여부 */}
        <View style={styles.inputGroup}>
            <Text style={styles.label}>알러지 여부</Text>
            <View style={styles.buttonRow}>
                <TouchableOpacity 
                    style={[styles.button, signUpForm.allergies === true && styles.buttonActive]}
                    onPress={() => handleSignUpChange('allergies', true)}
                >
                    <Text style={[styles.buttonText, signUpForm.allergies === true && styles.buttonTextActive]}>있음</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.button, signUpForm.allergies === false && styles.buttonActive]}
                    onPress={() => {
                        handleSignUpChange('allergies', false);
                        handleSignUpChange('allergies_detail', '');
                    }}
                >
                    <Text style={[styles.buttonText, signUpForm.allergies === false && styles.buttonTextActive]}>없음</Text>
                </TouchableOpacity>
            </View>
        </View>

        {/* 알러지 상세 정보 */}
        {signUpForm.allergies && (
            <View style={styles.inputGroup}>
                <Text style={styles.label}>알러지 상세 정보</Text>
                <TextInput
                    style={[styles.input, {height: 100}]}
                    value={signUpForm.allergies_detail}
                    onChangeText={(value) => handleSignUpChange('allergies_detail', value)}
                    placeholder="알러지 정보를 상세히 입력해주세요"
                    multiline
                />
            </View>
        )}

        {/* 회원가입 버튼 */}
        <TouchableOpacity 
            style={styles.submitButton}
            onPress={handleSignUpSubmit}
            disabled={signUpForm.password !== signUpForm.passwordConfirm}
        >
            <Text style={styles.submitButtonText}>회원가입</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB', // bg-gray-50
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: 'white',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#EC4899', // text-pink-500
  },
  formContainer: {
    flex: 1,
    paddingHorizontal: 16,
  },
  scrollContentContainer: {
    paddingTop: 16,
    paddingBottom: 100, // 키보드 여백을 위한 추가 패딩
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    color: '#374151', // text-gray-700
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F3F4F6', // bg-gray-100
    borderRadius: 12, // rounded-xl
    padding: 16,
    fontSize: 16,
  },
  errorText: {
    color: '#EF4444', // text-red-500
    fontSize: 12,
    marginTop: 4,
  },
  helperText: {
    color: '#6B7280', // text-gray-500
    fontSize: 12,
    marginTop: 4,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#F3F4F6', // border-gray-100
    backgroundColor: '#F3F4F6', // bg-gray-100
    alignItems: 'center',
    marginHorizontal: 4,
  },
  buttonActive: {
    backgroundColor: '#EC4899', // bg-pink-500
    borderColor: '#EC4899', // border-pink-500
  },
  buttonText: {
    color: '#374151', // text-gray-700
  },
  buttonTextActive: {
    color: 'white',
  },
  submitButton: {
    backgroundColor: '#EC4899', // bg-pink-500
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 48,
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
