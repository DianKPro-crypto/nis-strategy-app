import {Config} from '@remotion/cli/config';

// `assets/` is the single drop folder for photos, logo, music and JSON settings.
Config.setPublicDir('./assets');
Config.setEntryPoint('./src/index.ts');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(20);
Config.setAudioBitrate('192k');
Config.setOverwriteOutput(true);

// Optional: point Remotion at a pre-installed Chromium instead of downloading one.
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
