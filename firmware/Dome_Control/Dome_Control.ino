#include "ReelTwo.h"
#include "dome/Logics.h"
#include "dome/LogicEngineController.h"
#include "dome/HoloLights.h"
#include "dome/NeoPixelPSI.h"
#include "i2c/I2CReceiver.h"
 
I2CReceiver i2cReceiver(0x0a);

AstroPixelRLD<> RLD(LogicEngineRLDDefault, 1);
AstroPixelFLD<> FLD(LogicEngineFLDDefault, 2);

NeoPixelPSI rearPSI(4, 8);
NeoPixelPSI frontPSI(3, 8);

HoloLights frontHolo(10);
HoloLights rearHolo(12);
HoloLights topHolo(13);    

void setup()
{
    REELTWO_READY();
    SetupEvent::ready();
    Serial.begin(115200);
    Serial.println("Setting up");
    rearPSI.set_color(1, 0, 255, 0);  // Set the rear PSI colours
    rearPSI.set_color(2, 255, 255, 0);  // Without this it does the standard front colours
    rearPSI.set_speed(50);
    frontPSI.set_stickiness(20);
    frontPSI.set_speed(50);
    
    FLD.selectScrollTextLeft("R2\n    D2", LogicEngineRenderer::kBlue, 1, 15);
    RLD.selectScrollTextLeft("... AstroPixels ....", LogicEngineRenderer::kYellow, 0, 15);

}

void loop()
{
    AnimatedEvent::process();

}