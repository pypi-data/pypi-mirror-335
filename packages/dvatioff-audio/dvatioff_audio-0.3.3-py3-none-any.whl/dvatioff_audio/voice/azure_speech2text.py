import azure.cognitiveservices.speech as speechsdk
import time
import threading
from dvatioff_audio.utils import retry


# Azure STT 支持的语言
LANGUAGE = {
    "Chinese": "zh-CN",
    'English': "en-US",
    "Japanese": "ja-JP",
    'Korean': "ko-KR",
}


@retry(Exception, tries=10, delay=5)
def speech_to_text(audio_file, language, subscription, region):
    done = False
    text = ""

    def stop_cb(evt):
        nonlocal done
        print('CLOSING on {}'.format(evt))
        # 在新线程中执行 stop_continuous_recognition 以避免阻塞
        threading.Thread(target=speech_recognizer.stop_continuous_recognition).start()
        done = True

    def handle_result(evt):
        nonlocal text
        text += evt.result.text
        print('RECOGNIZED:', evt.result.text)

    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    speech_config.speech_recognition_language = LANGUAGE[language]
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    speech_recognizer.recognized.connect(handle_result)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    try:
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(0.1)

        if language == 'English':
            lower_text = text.lower()
            return lower_text

        return text
    except Exception as e:
        print(f"调用 Azure STT 接口时出错: {e}")
        return ""
