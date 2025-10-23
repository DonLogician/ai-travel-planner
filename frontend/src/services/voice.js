import apiClient from './api';

export const voiceService = {
  // Recognize speech from audio data
  async recognizeSpeech(audioData, language = 'zh_cn') {
    const response = await apiClient.post('/voice/recognize', {
      audio_data: audioData,
      language,
    });
    return response.data;
  },
};
