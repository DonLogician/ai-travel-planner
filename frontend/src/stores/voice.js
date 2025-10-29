import { defineStore } from 'pinia';

export const useVoiceStore = defineStore('voice', {
    state: () => ({
        isRecording: false,
        transcript: '',
        history: [],
        error: null,
    }),
    actions: {
        startRecording() {
            this.isRecording = true;
            this.transcript = '';
            this.error = null;
        },
        stopRecording() {
            this.isRecording = false;
        },
        appendTranscript(textSegment) {
            this.transcript = `${this.transcript}${textSegment}`.trim();
        },
        finalizeTranscript(payload) {
            this.history.unshift({
                text: payload.text,
                timestamp: payload.timestamp || new Date().toISOString(),
                intent: payload.intent || null,
            });
            this.transcript = payload.text;
        },
        setError(message) {
            this.error = message;
            this.isRecording = false;
        },
        reset() {
            this.isRecording = false;
            this.transcript = '';
            this.error = null;
        },
    },
});
