#include <RtAudio.h>

#include <iostream>

int main() {

   std::cout << "test start ..." << std::endl;

   try
   {
      RtAudio rtAudio;
   } catch (const RtAudioError& error)
   {
      error.printMessage();
   }

   std::cout << "test end ..." << std::endl;

   return 0;
}
