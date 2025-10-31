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

  // Upload recorded audio file for transcription
  async uploadVoice(file, language = 'zh_cn') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    const response = await apiClient.post('/voice/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};
