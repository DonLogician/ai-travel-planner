<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import { loadAmap } from '../services/mapLoader';

const props = defineProps({
	destination: {
		type: String,
		default: '',
	},
	dailyItinerary: {
		type: Array,
		default: () => [],
	},
	minHeight: {
		type: String,
		default: '460px',
	},
});

const mapContainer = ref(null);
const mapInstance = shallowRef(null);
const markers = shallowRef([]);
const infoWindow = shallowRef(null);
const isLoading = ref(true);
const loadError = ref('');

const FALLBACK_LOCATIONS = {
	beijing: {
		label: '北京',
		center: [116.407394, 39.904211],
		markers: [
			{
				name: '天安门广场',
				position: [116.403963, 39.915119],
				description: '首都地标，升旗仪式和人民英雄纪念碑所在。',
			},
			{
				name: '故宫博物院',
				position: [116.397451, 39.909167],
				description: '世界五大宫之首，建议预留半天参观。',
			},
			{
				name: '南锣鼓巷',
				position: [116.403318, 39.935169],
				description: '胡同漫步与传统小吃的热门街区。',
			},
			{
				name: '798 艺术区',
				position: [116.496847, 39.984104],
				description: '现代艺术园区，适合拍照与欣赏展览。',
			},
			{
				name: '慕田峪长城',
				position: [116.560509, 40.437437],
				description: '景观壮丽的长城段落，可乘坐索道上下。',
			},
		],
	},
};

const normalizeDestination = (raw) => (raw || '').trim().toLowerCase();

const hasValidCoordinates = (value) => Number.isFinite(value) && !Number.isNaN(value);

const extractActivityPoints = (days) => {
	if (!Array.isArray(days)) {
		return [];
	}

	const points = [];

	days.forEach((day, dayIndex) => {
		const activities = Array.isArray(day?.activities) ? day.activities : [];

		activities.forEach((activity, activityIndex) => {
			const candidate = activity || {};
			let lng;
			let lat;

			if (Array.isArray(candidate.coordinates) && candidate.coordinates.length >= 2) {
				[lng, lat] = candidate.coordinates.map(Number);
			} else if (
				hasValidCoordinates(candidate.longitude) &&
				hasValidCoordinates(candidate.latitude)
			) {
				lng = Number(candidate.longitude);
				lat = Number(candidate.latitude);
			} else if (hasValidCoordinates(candidate.lng) && hasValidCoordinates(candidate.lat)) {
				lng = Number(candidate.lng);
				lat = Number(candidate.lat);
			} else if (
				candidate.location &&
				typeof candidate.location === 'object' &&
				hasValidCoordinates(candidate.location.lng) &&
				hasValidCoordinates(candidate.location.lat)
			) {
				lng = Number(candidate.location.lng);
				lat = Number(candidate.location.lat);
			}

			if (hasValidCoordinates(lng) && hasValidCoordinates(lat)) {
				points.push({
					name:
						candidate.activity || candidate.title || candidate.name || `活动 ${dayIndex + 1}-${activityIndex + 1}`,
					position: [lng, lat],
					description: candidate.notes || candidate.description || candidate.detail || '',
					dayLabel: day?.day ? `第 ${day.day} 天` : '',
				});
			}
		});
	});

	return points;
};

const extractedPoints = computed(() => extractActivityPoints(props.dailyItinerary));

const wrapperStyles = computed(() => ({
	minHeight: props.minHeight || '460px',
}));

const fallbackKey = computed(() => {
	const normalized = normalizeDestination(props.destination);
	if (normalized.includes('beijing') || normalized.includes('北京')) {
		return 'beijing';
	}
	return 'beijing';
});

const resolvedMarkers = computed(() => {
	if (extractedPoints.value.length > 0) {
		return {
			cityLabel: props.destination || '行程地点',
			markers: extractedPoints.value,
			center: extractedPoints.value.length === 1 ? extractedPoints.value[0].position : null,
			usingFallback: false,
		};
	}

	const fallback = FALLBACK_LOCATIONS[fallbackKey.value] || FALLBACK_LOCATIONS.beijing;
	return {
		cityLabel: fallback.label,
		markers: fallback.markers,
		center: fallback.center,
		usingFallback: true,
	};
});

const hintMessage = computed(() => {
	if (loadError.value) {
		return '';
	}

	if (resolvedMarkers.value.usingFallback) {
		return props.destination
			? `暂未获取到 ${props.destination} 的具体地点，正展示北京示例点位。`
			: '目前展示北京示例行程，生成行程后将自动更新地点。';
	}

	return '';
});

const clearMarkers = () => {
	markers.value.forEach((marker) => marker.setMap(null));
	markers.value = [];
};

const buildMarkerContent = (point) => {
	const title = point.name || '地点';
	const day = point.dayLabel ? `<span class="day">${point.dayLabel}</span>` : '';
	const desc = point.description ? `<p class="desc">${point.description}</p>` : '';
	return `
		<div class="itinerary-map__popup">
			<strong>${title}</strong>
			${day}
			${desc}
		</div>
	`;
};

const updateMapMarkers = () => {
	const AMap = window.AMap;
	if (!mapInstance.value || !AMap) {
		return;
	}

	clearMarkers();

	const dataset = resolvedMarkers.value;
	if (!dataset.markers.length) {
		if (dataset.center) {
			mapInstance.value.setZoomAndCenter(10, dataset.center);
		}
		return;
	}

	const newMarkers = dataset.markers.map((point) => {
		const marker = new AMap.Marker({
			position: point.position,
			title: point.name,
			anchor: 'bottom-center',
			map: mapInstance.value,
		});

		if ((point.description && point.description.length) || point.dayLabel) {
			marker.on('click', () => {
				if (!infoWindow.value) {
					infoWindow.value = new AMap.InfoWindow({
						offset: new AMap.Pixel(0, -28),
						anchor: 'bottom-center',
					});
				}
				infoWindow.value.setContent(buildMarkerContent(point));
				infoWindow.value.open(mapInstance.value, marker.getPosition());
			});
		}

		return marker;
	});

	markers.value = newMarkers;

	if (newMarkers.length > 1) {
		mapInstance.value.setFitView(newMarkers, false, [60, 80, 60, 80]);
	} else if (newMarkers.length === 1) {
		mapInstance.value.setZoomAndCenter(12, newMarkers[0].getPosition());
	} else if (dataset.center) {
		mapInstance.value.setZoomAndCenter(10, dataset.center);
	}
};

onMounted(async () => {
	try {
		const AMap = await loadAmap();
		mapInstance.value = new AMap.Map(mapContainer.value, {
			zoom: 11,
			viewMode: '2D',
			resizeEnable: true,
			center: FALLBACK_LOCATIONS.beijing.center,
			mapStyle: 'amap://styles/whitesmoke',
		});

		mapInstance.value.on('click', () => {
			if (infoWindow.value) {
				infoWindow.value.close();
			}
		});

		isLoading.value = false;
		updateMapMarkers();
	} catch (error) {
		loadError.value = error?.message || '地图加载失败，请稍后重试。';
		isLoading.value = false;
	}
});

watch(
	() => [props.destination, props.dailyItinerary],
	() => {
		if (!isLoading.value && !loadError.value) {
			updateMapMarkers();
		}
	},
	{ deep: true }
);

watch(
	() => isLoading.value,
	(loading) => {
		if (!loading && !loadError.value) {
			updateMapMarkers();
		}
	}
);

onBeforeUnmount(() => {
	clearMarkers();
	if (mapInstance.value) {
		mapInstance.value.destroy();
		mapInstance.value = null;
	}
});
</script>

<template>
		<div class="itinerary-map" :style="wrapperStyles">
		<div ref="mapContainer" class="itinerary-map__canvas"></div>

		<div v-if="isLoading" class="itinerary-map__overlay">
			<span>地图加载中...</span>
		</div>

		<div v-else-if="loadError" class="itinerary-map__overlay itinerary-map__overlay--error">
			<p>{{ loadError }}</p>
			<p class="tip">请确认已配置 VITE_MAP_API_KEY，并可访问高德地图服务。</p>
		</div>

		<div v-else-if="hintMessage" class="itinerary-map__hint">
			{{ hintMessage }}
		</div>
	</div>
</template>

<style scoped>
.itinerary-map {
	position: relative;
	width: 100%;
	border-radius: 16px;
	overflow: hidden;
	background: #f1f3f5;
	min-height: 460px;
}

.itinerary-map__canvas {
	width: 100%;
	height: 100%;
	min-height: inherit;
}

.itinerary-map__overlay {
	position: absolute;
	inset: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.85);
	color: #333;
	font-weight: 600;
	text-align: center;
	padding: 1.5rem;
}

.itinerary-map__overlay--error {
	color: #c53030;
	flex-direction: column;
	gap: 0.75rem;
	font-weight: 500;
}

.itinerary-map__overlay--error .tip {
	font-size: 0.9rem;
	color: #4a5568;
}

.itinerary-map__hint {
	position: absolute;
	left: 1rem;
	top: 1rem;
	max-width: calc(100% - 2rem);
	padding: 0.75rem 1rem;
	background: rgba(102, 126, 234, 0.15);
	color: #2c3e50;
	border-radius: 12px;
	font-size: 0.95rem;
	line-height: 1.4;
	backdrop-filter: blur(6px);
	box-shadow: 0 8px 18px rgba(102, 126, 234, 0.18);
}

.itinerary-map__popup {
	min-width: 180px;
	max-width: 220px;
	color: #1a202c;
}

.itinerary-map__popup strong {
	display: block;
	margin-bottom: 0.25rem;
}

.itinerary-map__popup .day {
	display: inline-block;
	margin-bottom: 0.25rem;
	padding: 0.1rem 0.4rem;
	font-size: 0.75rem;
	color: #4c51bf;
	background: rgba(102, 126, 234, 0.1);
	border-radius: 999px;
}

.itinerary-map__popup .desc {
	margin: 0;
	font-size: 0.85rem;
	color: #4a5568;
	line-height: 1.4;
}

@media (max-width: 1024px) {
	.itinerary-map {
		min-height: 360px;
	}
}
</style>
