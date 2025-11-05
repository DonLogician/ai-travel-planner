const AMAP_SCRIPT_ID = 'amap-sdk';
let loadPromise = null;

function injectScript(key) {
    if (typeof document === 'undefined') {
        return Promise.reject(new Error('Map SDK 只能在浏览器环境中加载。'));
    }

    if (!key) {
        return Promise.reject(new Error('缺少 VITE_MAP_API_KEY，无法加载高德地图。'));
    }

    if (document.getElementById(AMAP_SCRIPT_ID)) {
        return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.id = AMAP_SCRIPT_ID;
        script.type = 'text/javascript';
        script.async = true;
        script.defer = true;
        script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(
            key
        )}&plugin=AMap.Geocoder`;

        script.onload = () => resolve();
        script.onerror = () => reject(new Error('高德地图脚本加载失败，请检查网络或 API Key。'));

        document.head.appendChild(script);
    });
}

export async function loadAmap() {
    if (typeof window !== 'undefined' && window.AMap) {
        return window.AMap;
    }

    if (!loadPromise) {
        const key = import.meta.env.VITE_MAP_API_KEY;
        loadPromise = injectScript(key).then(() => {
            if (!window.AMap) {
                throw new Error('高德地图未正确加载，请稍后重试。');
            }
            return window.AMap;
        });
    }

    return loadPromise;
}
