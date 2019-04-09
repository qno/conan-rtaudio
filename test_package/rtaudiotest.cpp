#include <RtAudio.h>

int main() {

   try
   {
      RtAudio rtAudio;
   } catch (const RtAudioError& error)
   {
      error.printMessage();
   }

   return 0;
}
