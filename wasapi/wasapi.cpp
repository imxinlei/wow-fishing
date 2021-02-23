#include <iostream>
#include <exception>
#include <Mmdeviceapi.h>
#include <Audioclient.h>
#include <audiopolicy.h>

//-----------------------------------------------------------
// Record an audio stream from the default audio capture
// device. The RecordAudioStream function allocates a shared
// buffer big enough to hold one second of PCM audio data.
// The function uses this buffer to stream data from the
// capture device. The main loop runs every 1/2 second.
//-----------------------------------------------------------

// REFERENCE_TIME time units per second and per millisecond
#define REFTIMES_PER_SEC  10000000
#define REFTIMES_PER_MILLISEC  10000

#define THROW_ON_ERROR(rs, err) \
  if (FAILED(rs)) { \
    std::cout << "error code: " << hr << std::endl; \
    throw std::exception(err); \
  }

#define SAFE_RELEASE(punk) \
  if ((punk) != NULL) { (punk)->Release(); (punk) = NULL; }

const CLSID CLSID_MMDeviceEnumerator = __uuidof(MMDeviceEnumerator);
const IID IID_IMMDeviceEnumerator = __uuidof(IMMDeviceEnumerator);
const IID IID_IAudioClient = __uuidof(IAudioClient);
const IID IID_IAudioCaptureClient = __uuidof(IAudioCaptureClient);

class WasapiReader {

  public:

    void start() {
      CoInitialize(NULL);

      hr = CoCreateInstance(
        CLSID_MMDeviceEnumerator,
        NULL,
        CLSCTX_ALL,
        IID_IMMDeviceEnumerator,
        (void**)&pEnumerator
      );
      THROW_ON_ERROR(hr, "create Enumerator failed.");

      hr = pEnumerator->GetDefaultAudioEndpoint(
        eRender,
        eConsole,
        &pDevice
      );
      THROW_ON_ERROR(hr, "GetDefaultAudioEndpoint failed.");

      hr = pDevice->Activate(
        IID_IAudioClient,
        CLSCTX_ALL,
        NULL,
        (void**)&pAudioClient
      );
      THROW_ON_ERROR(hr, "activate device failed.");

      hr = pAudioClient->GetMixFormat(&pwfx);
      THROW_ON_ERROR(hr, "get mix format failed.");

      if (pwfx->wFormatTag == WAVE_FORMAT_EXTENSIBLE) {
        PWAVEFORMATEXTENSIBLE pEx = reinterpret_cast<PWAVEFORMATEXTENSIBLE>(pwfx);

        if (pEx->SubFormat == KSDATAFORMAT_SUBTYPE_IEEE_FLOAT) {
          std::cout << "format is KSDATAFORMAT_SUBTYPE_IEEE_FLOAT" << std::endl;
        } else {
          std::cout << "format is not KSDATAFORMAT_SUBTYPE_IEEE_FLOAT" << std::endl;
          throw std::exception("format is not KSDATAFORMAT_SUBTYPE_IEEE_FLOAT");
        }
      } else {
        std::cout << "format is not WAVE_FORMAT_EXTENSIBLE" << std::endl;
        throw std::exception("format is not WAVE_FORMAT_EXTENSIBLE");
      }

      std::cout << "audio format: " << std::endl
        << "format tag: " << pwfx->wFormatTag << std:: endl
        << "channels: " << pwfx->nChannels << std:: endl
        << "samples per second: " << pwfx->nSamplesPerSec << std:: endl
        << "average bytes per second: " << pwfx->nAvgBytesPerSec << std:: endl
        << "block size: " << pwfx->nBlockAlign << std:: endl
        << "bits per sample: " << pwfx->wBitsPerSample << std:: endl;

      hr = pAudioClient->Initialize(
        AUDCLNT_SHAREMODE_SHARED,
        AUDCLNT_STREAMFLAGS_LOOPBACK,
        hnsRequestedDuration,
        0,
        pwfx,
        NULL
      );
      THROW_ON_ERROR(hr, "initialize audio client failed.");

      hr = pAudioClient->GetBufferSize(&bufferFrameCount);
      THROW_ON_ERROR(hr, "get buffer size failed.");

      hr = pAudioClient->GetService(
        IID_IAudioCaptureClient,
        (void**)&pCaptureClient
      );
      THROW_ON_ERROR(hr, "get audio capture client service failed.");

      hr = pAudioClient->Start();
      THROW_ON_ERROR(hr, "start recording failed.");
    }

    void stop() {
      hr = pAudioClient->Stop();
      THROW_ON_ERROR(hr, "stop recording failed.");
      dispose();
    }

    float peakVolume() {
      float maxVolume = 0.0;

      hr = pCaptureClient->GetNextPacketSize(&packetLength);
      THROW_ON_ERROR(hr, "get next packet size failed.");

      while (packetLength != 0) {
        hr = pCaptureClient->GetBuffer(
          &pData,
          &numFramesAvailable,
          &flags, NULL, NULL);
        THROW_ON_ERROR(hr, "get buffer failed.");

        if (flags & AUDCLNT_BUFFERFLAGS_SILENT) {
            pData = NULL;  // Tell CopyData to write silence.
        } else {
          for (int i = 0; i < packetLength; i++) {
            float* v = (float*)pData + i * 2;
            maxVolume = max(maxVolume, *v);
          }
        }

        hr = pCaptureClient->ReleaseBuffer(numFramesAvailable);
        THROW_ON_ERROR(hr, "release buffer failed.");

        hr = pCaptureClient->GetNextPacketSize(&packetLength);
        THROW_ON_ERROR(hr, "get next packet size failed.");
      }

      return maxVolume;
    }

    void dispose() {
      CoTaskMemFree(pwfx);
      SAFE_RELEASE(pEnumerator)
      SAFE_RELEASE(pDevice)
      SAFE_RELEASE(pAudioClient)
      SAFE_RELEASE(pCaptureClient)
    }
  private:

    IMMDeviceEnumerator *pEnumerator = NULL;
    IMMDevice *pDevice = NULL;
    IAudioClient *pAudioClient = NULL;
    IAudioCaptureClient *pCaptureClient = NULL;
    WAVEFORMATEX *pwfx = NULL;

    HRESULT hr;
    REFERENCE_TIME hnsRequestedDuration = REFTIMES_PER_SEC;
    REFERENCE_TIME hnsActualDuration;
    UINT32 bufferFrameCount;
    UINT32 numFramesAvailable;

    UINT32 packetLength = 0;
    BOOL bDone = FALSE;
    BYTE *pData;
    DWORD flags;

};

WasapiReader reader;

extern "C" __declspec(dllexport) int startCapture(int a) {
  try {
    reader.start();
  } catch(const std::exception& err) {
    reader.dispose();
    std::cout << err.what() << std::endl;
    return -1;
  }
  return 0;
}

extern "C" __declspec(dllexport) int stopCapture() {
  try {
    reader.stop();
  } catch(const std::exception& err) {
    reader.dispose();
    std::cout << err.what() << std::endl;
    return -1;
  }
  return 0;
}

extern "C" __declspec(dllexport) float peakVolume() {
  try {
    return reader.peakVolume();
  } catch(const std::exception& err) {
    std::cout << err.what() << std::endl;
    return 0;
  }
}
