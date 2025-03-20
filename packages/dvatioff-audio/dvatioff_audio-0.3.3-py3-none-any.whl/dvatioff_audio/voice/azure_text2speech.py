import azure.cognitiveservices.speech as speechsdk
from dvatioff_audio.utils import retry


# Azure TTS 语音模板
VOICE_TEMPLATE = {
    "Chinese": "zh-CN-XiaoxiaoNeural",
    "English": "en-US-JennyNeural",
    "Korean": "ko-KR-SunHiNeural",
    "Japanese": "ja-JP-NanamiNeural",
}


@retry(Exception, tries=10, delay=1)
def text2speech(text, language, path, subscription, region):
    try:
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False, filename=path)

        # The language of the voice that speaks.
        speech_config.speech_synthesis_voice_name = VOICE_TEMPLATE[language]
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        # Get text from the console and synthesize to the default speaker.
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("AI占位语音生成中： [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")
    except Exception as e:
        print(f"调用 Azure TTS 接口时出错: {e}")
        raise
