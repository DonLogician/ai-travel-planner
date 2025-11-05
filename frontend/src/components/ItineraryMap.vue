<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { loadAmap } from '../services/mapLoader';

const locationCache = new Map();

const props = defineProps({
  destination: { type: String, default: '' },
  points: { type: Array, default: () => [] },
  autoFit: { type: Boolean, default: true },
  emptyText: { type: String, default: '暂时没有可展示的地点。' },
  loadingText: { type: String, default: '地图加载中...' },
});

const mapElement = ref(null);
const mapInstance = ref(null);
const amapApi = ref(null);
const geocoder = ref(null);
const infoWindow = ref(null);
const mapReady = ref(false);
const loading = ref(true);
const error = ref(null);
const helperMessage = ref('正在初始化地图...');
const markers = ref([]);
let updateToken = 0;

const normalizedPoints = computed(() => {
  return props.points
    .map((item, index) => {
      if (!item) {
        return null;
      }

      const latCandidates = [
        item.latitude,
        item.lat,
        item.latLng?.lat,
        item.location?.lat,
        item.position?.lat,
      ];
      const lngCandidates = [
        item.longitude,
        item.lng,
        item.latLng?.lng,
        item.location?.lng,
        item.position?.lng,
      ];

      const latitude = extractNumber(latCandidates);
      const longitude = extractNumber(lngCandidates);
      const locationName = (item.location || item.name || '').trim();
      const label = (item.title || item.activity || locationName || `地点 ${index + 1}`).trim();

      if (!label) {
        return null;
      }

      return {
        id: item.id ?? `${index}-${label}`,
        label,
        locationName,
        day: item.day ?? null,
        time: item.time ?? null,
        notes: item.notes ?? '',
        latitude,
        longitude,
      };
    })
    .filter(Boolean)
    .slice(0, 40);
});

function extractNumber(candidates) {
  for (const candidate of candidates) {
    const parsed = Number(candidate);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return null;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

onMounted(async () => {
  try {
    const AMap = await loadAmap();
    amapApi.value = AMap;
    mapInstance.value = new AMap.Map(mapElement.value, {
      viewMode: '3D',
      zoom: 10,
      resizeEnable: true,
      center: [116.397428, 39.90923],
    });
    geocoder.value = new AMap.Geocoder();
    infoWindow.value = new AMap.InfoWindow({
      offset: new AMap.Pixel(0, -24),
    });
    mapReady.value = true;
    loading.value = false;
    helperMessage.value = props.emptyText;
    await updateMap();
  } catch (err) {
    error.value = err?.message || '高德地图加载失败，请检查网络或 API Key。';
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  if (markers.value.length && mapInstance.value) {
    mapInstance.value.remove(markers.value);
  }
  markers.value = [];
  if (mapInstance.value) {
    mapInstance.value.destroy();
    mapInstance.value = null;
  }
});

watch(
  [() => props.destination, normalizedPoints],
  () => {
    if (!mapReady.value) {
      return;
    }
    updateMap();
  },
  { deep: true }
);

async function updateMap() {
  if (!mapReady.value || !mapInstance.value || !amapApi.value) {
    return;
  }

  loading.value = true;
  error.value = null;
  helperMessage.value = '';

  if (markers.value.length) {
    mapInstance.value.remove(markers.value);
    markers.value = [];
  }
  infoWindow.value?.close();

  const token = ++updateToken;
  const resolvedMarkers = [];

  for (const point of normalizedPoints.value) {
    if (token !== updateToken) {
      return;
    }

    const lnglat = await resolveLngLat(point, token);

    if (!lnglat || token !== updateToken) {
      continue;
    }

    const marker = new amapApi.value.Marker({
      map: mapInstance.value,
      position: lnglat,
      title: point.label,
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
      offset: new amapApi.value.Pixel(-13, -30),
    });

    marker.setExtData({ ...point, lnglat });
    marker.on('click', () => openInfoWindow(marker));
    markers.value.push(marker);
    resolvedMarkers.push(marker);
  }

  if (token !== updateToken) {
    return;
  }

  if (resolvedMarkers.length) {
    if (props.autoFit) {
      mapInstance.value.setFitView(resolvedMarkers, true, [60, 60, 60, 60]);
    }
    helperMessage.value = '';
  } else {
    await focusOnDestination(token);
  }

  loading.value = false;
}

async function resolveLngLat(point, token) {
  if (!amapApi.value) {
    return null;
  }

  if (Number.isFinite(point.longitude) && Number.isFinite(point.latitude)) {
    return [point.longitude, point.latitude];
  }

  if (!point.locationName) {
    return null;
  }

  const query = point.locationName.trim();
  if (!query) {
    return null;
  }

  const cached = locationCache.get(query);
  if (cached) {
    if (typeof cached.then === 'function') {
      return cached;
    }
    return cached;
  }

  const promise = new Promise((resolve) => {
    geocoder.value?.getLocation(query, (status, result) => {
      if (token !== updateToken) {
        resolve(null);
        return;
      }

      if (status === 'complete' && result?.geocodes?.length) {
        const { location } = result.geocodes[0];
        if (location) {
          resolve([location.lng, location.lat]);
          return;
        }
      }
      resolve(null);
    });
  }).then((value) => {
    if (value) {
      locationCache.set(query, value);
    } else {
      locationCache.delete(query);
    }
    return value;
  });

  locationCache.set(query, promise);
  return promise;
}

async function focusOnDestination(token) {
  const name = (props.destination || '').trim();
  if (!name) {
    helperMessage.value = props.emptyText;
    return;
  }

  try {
    mapInstance.value.setCity(name);
    mapInstance.value.setZoom(11);
    helperMessage.value = `已定位到 ${name}，等待地点坐标。`;
  } catch (err) {
    const lnglat = await geocodeDestination(name, token);
    if (lnglat && token === updateToken) {
      mapInstance.value.setCenter(lnglat);
      mapInstance.value.setZoom(11);
      helperMessage.value = `已定位到 ${name}，可以继续完善行程地点。`;
    } else if (token === updateToken) {
      helperMessage.value = props.emptyText;
    }
  }
}

function geocodeDestination(name, token) {
  const query = name.trim();
  if (!query) {
    return Promise.resolve(null);
  }
  return resolveLngLat({ locationName: query }, token);
}

function openInfoWindow(marker) {
  if (!infoWindow.value || !mapInstance.value) {
    return;
  }

  const data = marker.getExtData() || {};
  const lines = [];
  lines.push(`<strong>${escapeHtml(data.label)}</strong>`);
  if (data.day) {
    lines.push(`<div>第 ${escapeHtml(data.day)} 天 ${escapeHtml(data.time || '')}</div>`);
  } else if (data.time) {
    lines.push(`<div>${escapeHtml(data.time)}</div>`);
  }
  if (data.locationName) {
    lines.push(`<div>📍 ${escapeHtml(data.locationName)}</div>`);
  }
  if (data.notes) {
    lines.push(`<div class="notes">${escapeHtml(data.notes)}</div>`);
  }

  infoWindow.value.setContent(`<div class="map-info-window">${lines.join('')}</div>`);
  infoWindow.value.open(mapInstance.value, marker.getPosition());
}
</script>

<template>
  <div class="itinerary-map">
    <div ref="mapElement" class="map-canvas"></div>

    <transition name="fade">
      <div v-if="loading" class="map-overlay">{{ loadingText }}</div>
    </transition>

    <transition name="fade">
      <div v-if="!loading && error" class="map-overlay error">{{ error }}</div>
    </transition>

    <transition name="fade">
      <div v-if="!loading && !error && helperMessage" class="map-overlay helper">
        {{ helperMessage }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
.itinerary-map {
  position: relative;
  width: 100%;
  min-height: 420px;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border: 1px solid #e5e7eb;
}

.map-canvas {
  width: 100%;
  height: 100%;
}

.map-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.86);
  color: #334155;
  font-weight: 600;
  backdrop-filter: blur(2px);
}

.map-overlay.error {
  color: #b91c1c;
  background: rgba(254, 226, 226, 0.92);
}

.map-overlay.helper {
  color: #475569;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

:deep(.map-info-window) {
  font-size: 0.95rem;
  color: #1f2937;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

:deep(.map-info-window .notes) {
  color: #64748b;
  font-size: 0.85rem;
}
</style>
