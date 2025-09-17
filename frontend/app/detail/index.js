//frontend/app/detail/index.js

import { useLocalSearchParams, useRouter } from 'expo-router';
import DetailScreen from '../../components/DetailScreen';

export default function DetailScreenWithLogic() {
    const router = useRouter();
    const params = useLocalSearchParams();
    const { id, name, rating, reviews, image, description, tags } = params;

    // 더미 데이터 추가 (필요한 경우)
    const mockData = {
        id: id,
        name: name,
        rating: rating,
        reviews: reviews,
        image: image,
        description: description,
        tags: tags ? tags.split(',') : [],
        address: '123 Main St, Anytown USA',
        hours: 'Mon-Sun: 10:00 AM - 10:00 PM',
        phone: '555-1234',
        details: 'A cozy spot for all your coffee needs. Enjoy our special blend, light snacks, and a relaxing atmosphere. Free Wi-Fi available.'
    };

    const handleBack = () => {
        router.back();
    };

    return <DetailScreen data={mockData} onBack={handleBack} />;
}
