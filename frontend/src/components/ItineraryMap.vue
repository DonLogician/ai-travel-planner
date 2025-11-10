<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import AMapLoader from '@amap/amap-jsapi-loader';

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
const AMapRef = shallowRef(null);
const isLoading = ref(true);
const loadError = ref('');
const placeSearchInstance = shallowRef(null);
const geocoderInstance = shallowRef(null);
const destinationMeta = ref({ keyword: '', coords: null });
const destinationSearchCounter = ref(0);
const destinationCache = new Map();
const activityMarkers = shallowRef([]);
const infoWindow = shallowRef(null);
const activityAddressCache = new Map();
const DEFAULT_CENTER = [116.407394, 39.904211];
const normalizeDestinationKeyword = (raw) => {
	const value = (raw || '').trim();
	if (!value) {
		console.log('[ItineraryMap] normalizeDestinationKeyword: empty input');
		return '';
	}
	if (/[\u4e00-\u9fa5]+(市|省|区|县|州|自治区)$/.test(value)) {
		return value;
	}
	return `${value}市`;
};

const wrapperStyles = computed(() => ({
	minHeight: props.minHeight || '460px',
}));

const hasValidCoordinates = (value) => Number.isFinite(value) && !Number.isNaN(value);

const sightseeingActivities = computed(() => {
	if (!Array.isArray(props.dailyItinerary)) {
		return [];
	}

	const results = [];

	props.dailyItinerary.forEach((day, dayIndex) => {
		const activities = Array.isArray(day?.activities) ? day.activities : [];
		activities.forEach((activity, activityIndex) => {
			if (!activity || !activity.is_sightseeing || !activity.location_address) {
				return;
			}

			const candidate = activity;
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

			const coords =
				hasValidCoordinates(lng) && hasValidCoordinates(lat) ? [lng, lat] : null;

			results.push({
				key: `${dayIndex}-${activityIndex}-${candidate.activity || candidate.title || candidate.name || activityIndex}`,
				name:
					candidate.activity || candidate.title || candidate.name || `活动 ${dayIndex + 1}-${activityIndex + 1}`,
				address: String(candidate.location_address).trim(),
				description: candidate.notes || candidate.description || candidate.detail || '',
				dayLabel: day?.day ? `第 ${day.day} 天` : '',
				coords,
			});
		});
	});

	return results;
});
const updateMapCenter = async () => {
	if (!mapInstance.value) {
		return;
	}

	let center = destinationMeta.value.coords;

	if (!center && props.destination) {
		center = await ensureDestinationCenter();
	}

	if (center) {
		mapInstance.value.setZoomAndCenter(11, center);
	}
};

const refreshMap = async () => {
	await updateMapCenter();
	await updateActivityMarkers();
};

const clearActivityMarkers = () => {
	activityMarkers.value.forEach((marker) => marker.setMap(null));
	activityMarkers.value = [];
};

const buildActivityPopup = (item) => {
	const title = item.name || '景点';
	const day = item.dayLabel ? `<span class="day">${item.dayLabel}</span>` : '';
	const address = item.address ? `<p class="addr">${item.address}</p>` : '';
	const desc = item.description ? `<p class="desc">${item.description}</p>` : '';
	return `
		<div class="itinerary-map__popup">
			<strong>${title}</strong>
			${day}
			${address}
			${desc}
		</div>
	`;
};

const resolveActivityCoordinates = async (item) => {
	if (item.coords) {
		return item.coords;
	}

	const address = item.address;
	if (!address) {
		return null;
	}

	const normalizedAddress = address.trim();
	if (!normalizedAddress) {
		return null;
	}

	if (activityAddressCache.has(normalizedAddress)) {
		return activityAddressCache.get(normalizedAddress);
	}

	if (!geocoderInstance.value) {
		return null;
	}

	const coords = await new Promise((resolve) => {
		geocoderInstance.value.getLocation(normalizedAddress, (status, result) => {
			if (status === 'complete' && result?.geocodes?.length) {
				const best = result.geocodes.find((geo) => geo?.level && geo.level.includes('兴趣点'))
					|| result.geocodes[0];
				if (best?.location?.lng && best?.location?.lat) {
					return resolve([
						Number(best.location.lng),
						Number(best.location.lat),
					]);
				}
			}
			resolve(null);
		});
	});

	activityAddressCache.set(normalizedAddress, coords);
	return coords;
};

const updateActivityMarkers = async () => {
	console.log('[ItineraryMap] 更新活动标记');
	if (!mapInstance.value || !AMapRef.value) {
		console.log('[ItineraryMap] updateActivityMarkers: mapInstance or AMapRef not ready');
		return;
	}

	clearActivityMarkers();

	const activities = sightseeingActivities.value;
	if (!activities.length) {
		console.log('[ItineraryMap] 无需添加活动标记');
		return;
	}

	const resolvedActivities = [];
	console.log('[ItineraryMap] 解析活动坐标，活动数量:', activities.length);
	// for (const activity of activities) {
	// 	// eslint-disable-next-line no-await-in-loop
	// 	const coords = await resolveActivityCoordinates(activity);
	// 	if (coords) {
	// 		resolvedActivities.push({ ...activity, coords });
	// 	}
	// }
	for (let i = 0; i < activities.length; i++) {
		const activity = activities[i];
		console.log(`[ItineraryMap] 处理第 ${i + 1} 个活动:`, activity.name || '未命名活动');
		
		try {
			// 添加超时保护
			const coords = await Promise.race([
				resolveActivityCoordinates(activity),
				new Promise((_, reject) => 
					setTimeout(() => reject(new Error(`解析活动坐标超时: ${activity.name}`)), 5000)
				)
			]);
			
			if (coords) {
				resolvedActivities.push({ ...activity, coords });
				console.log(`[ItineraryMap] 活动坐标解析成功:`, coords);
			} else {
				console.log(`[ItineraryMap] 活动坐标解析返回空值`);
			}
		} catch (error) {
			console.error(`[ItineraryMap] 解析活动坐标失败:`, error);
			// 继续处理下一个活动，不中断循环
		}
	}
	console.log('[ItineraryMap] 解析完成，有效活动数:', resolvedActivities.length);

	if (!resolvedActivities.length) {
		console.log('[ItineraryMap] 无有效活动坐标，跳过添加标记');
		return;
	}

	const markers = resolvedActivities.map((item) => {
		const marker = new AMapRef.value.Marker({
			position: item.coords,
			map: mapInstance.value,
			title: item.name,
		});
		marker.setExtData(item);
		marker.on('click', () => {
			const AMap = AMapRef.value;
			if (!AMap) {
				console.log('[ItineraryMap] Marker click: AMapRef not ready');
				return;
			}
			if (!infoWindow.value) {
				const { InfoWindow, Pixel } = AMap;
				infoWindow.value = new InfoWindow({
					offset: new Pixel(0, -28),
					anchor: 'bottom-center',
				});
			}
			infoWindow.value.setContent(buildActivityPopup(item));
			infoWindow.value.open(mapInstance.value, marker.getPosition());
		});
		console.log('[ItineraryMap] 添加标记:', item.name, item.coords);
		return marker;
	});

	activityMarkers.value = markers;
	console.log('[ItineraryMap] 添加活动标记:', markers.length);
};

const ensureDestinationCenter = async () => {
	const keyword = normalizeDestinationKeyword(props.destination);
	if (!keyword) {
		destinationMeta.value = { keyword: '', coords: null };
		console.log('[ItineraryMap] 跳过空目的地');
		return null;
	}

	if (destinationCache.has(keyword)) {
		const cached = destinationCache.get(keyword);
		destinationMeta.value = { keyword, coords: cached };
		console.log('[ItineraryMap] 使用缓存目的地中心:', keyword, cached);
		return cached;
	}

	const token = destinationSearchCounter.value + 1;
	destinationSearchCounter.value = token;
	console.log('[ItineraryMap] 开始定位目的地:', keyword);

	const coords = await resolveDestinationCenter(keyword);

	destinationCache.set(keyword, coords);
	if (destinationSearchCounter.value === token) {
		destinationMeta.value = { keyword, coords };
	}

	console.log('[ItineraryMap] 定位结果:', keyword, coords);
	return coords;
};

const resolveDestinationCenter = async (keyword) => {
	if (!geocoderInstance.value && !placeSearchInstance.value) {
		return null;
	}

	// Prefer Geocoder for city/province keywords to get administrative center
	if (geocoderInstance.value) {
		const candidateKeywords = [];
		const isChineseKeyword = /[\u4e00-\u9fa5]/.test(keyword);
		const hasAdministrativeSuffix = /(市|省|区|县|州|自治区)$/.test(keyword);
		if (isChineseKeyword && !hasAdministrativeSuffix) {
			candidateKeywords.push(`${keyword}市`);
		}
		candidateKeywords.push(keyword);

		for (const candidate of candidateKeywords) {
			console.log('[ItineraryMap] Geocoder 尝试:', candidate);
			// eslint-disable-next-line no-await-in-loop
			const geocodeResult = await new Promise((resolve) => {
				geocoderInstance.value.getLocation(candidate, (status, result) => {
					if (status === 'complete' && result?.geocodes?.length) {
						const adminResult = result.geocodes.find((geo) => {
							if (!geo.level) {
								return false;
							}
							return ['省', '市', '区县'].some((level) => geo.level.includes(level));
						});
						const item = adminResult || result.geocodes[0];
						if (item?.location?.lng && item?.location?.lat) {
							return resolve([
								Number(item.location.lng),
								Number(item.location.lat),
							]);
						}
					}
					resolve(null);
				});
			});

			if (geocodeResult) {
				console.log('[ItineraryMap] Geocoder 成功:', candidate, geocodeResult);
				return geocodeResult;
			}
		}
	}

	if (placeSearchInstance.value) {
		return new Promise((resolve) => {
			console.log('[ItineraryMap] PlaceSearch 尝试:', keyword);
			placeSearchInstance.value.search(keyword, (status, result) => {
				let center = null;
				if (status === 'complete' && result?.poiList?.pois?.length) {
					const candidatePoi = result.poiList.pois.find((poi) => {
						const type = poi?.type || '';
						const name = poi?.name || '';
						return (
							type.includes('政府') ||
							type.includes('中心') ||
							name.includes('市政府') ||
							name.includes('中心')
						);
					}) ||
					result.poiList.pois.find(
						(poi) => poi?.location?.lng && poi?.location?.lat
					);

					if (candidatePoi?.location?.lng && candidatePoi?.location?.lat) {
						center = [
							Number(candidatePoi.location.lng),
							Number(candidatePoi.location.lat),
						];
						console.log('[ItineraryMap] PlaceSearch 命中:', candidatePoi.name, center);
					}
				}
					if (!center) {
					console.warn('[ItineraryMap] PlaceSearch 无结果:', keyword);
					}
				resolve(center);
			});
		});
	}

	return null;
};

onMounted(async () => {
	console.log('[DEBUG] 组件开始挂载');
	console.log('[DEBUG] props.destination:', props.destination);
	console.log('[DEBUG] props.dailyItinerary:', props.dailyItinerary);
	const apiKey = import.meta.env.VITE_MAP_API_KEY;
	if (!apiKey) {
		loadError.value = '缺少 VITE_MAP_API_KEY，无法加载高德地图。';
		isLoading.value = false;
		return;
	}

	const securityCode = import.meta.env.VITE_MAP_SECURITY_CODE;
	if (securityCode && typeof window !== 'undefined') {
		window._AMapSecurityConfig = {
			securityJsCode: securityCode,
		};
	}

	try {
		const AMap = await AMapLoader.load({
			key: apiKey,
			version: '2.0',
			plugins: ['AMap.PlaceSearch', 'AMap.Geocoder'],
		});

		AMapRef.value = AMap;
		mapInstance.value = new AMap.Map(mapContainer.value, {
			zoom: 11,
			viewMode: '2D',
			resizeEnable: true,
			center: DEFAULT_CENTER,
			mapStyle: 'amap://styles/whitesmoke',
		});

		placeSearchInstance.value = new AMap.PlaceSearch({
			city: '',
			pageSize: 5,
			pageIndex: 1,
		});

		const geocoderCity = normalizeDestinationKeyword(props.destination);
		geocoderInstance.value = new AMap.Geocoder({
			city: geocoderCity || '',
			radius: 1000,
			batch: false,
		});

		mapInstance.value.on('click', () => {
			if (infoWindow.value) {
				infoWindow.value.close();
			}
		});

		isLoading.value = false;
		await refreshMap();
	} catch (error) {
		loadError.value = error?.message || '高德地图加载失败，请稍后重试。';
		isLoading.value = false;
	}
});

watch(
	() => [props.destination, props.dailyItinerary],
	() => {
		if (!isLoading.value && !loadError.value) {
			Promise.resolve()
				.then(() => refreshMap())
				.catch((error) => {
					console.error('刷新地图失败:', error);
				});
		}
	},
	{ deep: true }
);

watch(
	() => isLoading.value,
	(loading) => {
		if (!loading && !loadError.value) {
			Promise.resolve()
				.then(() => refreshMap())
				.catch((error) => {
					console.error('刷新地图失败:', error);
				});
		}
	}
);

watch(
	() => props.destination,
	() => {
		destinationMeta.value = { keyword: '', coords: null };
		activityAddressCache.clear();
		clearActivityMarkers();
		const keyword = normalizeDestinationKeyword(props.destination);
		if (placeSearchInstance.value) {
			placeSearchInstance.value.setCity(keyword || '');
		}
		if (geocoderInstance.value) {
			geocoderInstance.value.setCity(keyword || '');
		}
		destinationSearchCounter.value += 1;

		if (keyword) {
			// Schedule destination centering separately so it doesn't block the watcher flush
			Promise.resolve()
				.then(() => ensureDestinationCenter())
				.then(() => updateActivityMarkers())
				.catch((error) => {
					console.warn('[ItineraryMap] 目的地定位失败:', keyword, error);
				});
		}
	}
);

onBeforeUnmount(() => {
	clearActivityMarkers();
	if (infoWindow.value) {
		infoWindow.value.close();
		infoWindow.value = null;
	}
	if (mapInstance.value) {
		mapInstance.value.destroy();
		mapInstance.value = null;
	}
	destinationCache.clear();
	geocoderInstance.value = null;
	placeSearchInstance.value = null;
	AMapRef.value = null;
	activityAddressCache.clear();
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

.itinerary-map__popup {
	min-width: 200px;
	max-width: 240px;
	color: #1a202c;
}

.itinerary-map__popup strong {
	display: block;
	margin-bottom: 0.25rem;
}

.itinerary-map__popup .day {
	display: inline-block;
	margin-bottom: 0.3rem;
	padding: 0.15rem 0.45rem;
	font-size: 0.75rem;
	color: #4c51bf;
	background: rgba(102, 126, 234, 0.12);
	border-radius: 999px;
}

.itinerary-map__popup .addr {
	margin: 0;
	font-size: 0.85rem;
	color: #2d3748;
	line-height: 1.45;
}

.itinerary-map__popup .desc {
	margin: 0.35rem 0 0;
	font-size: 0.83rem;
	color: #4a5568;
	line-height: 1.4;
}

@media (max-width: 1024px) {
	.itinerary-map {
		min-height: 360px;
	}
}
</style>
