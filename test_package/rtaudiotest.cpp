#include <RtAudio.h>

#include <iostream>

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
