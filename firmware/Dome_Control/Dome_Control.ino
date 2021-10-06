#define USE_DEBUG
#include "ReelTwo.h"
#include "dome/Logics.h"
#include "dome/HoloLights.h"
#include "dome/LogicEngineController.h"
#include "dome/NeoPixelPSI.h"
#include "i2c/I2CReceiver.h"

LogicEngineDeathStarFLD<> FLD(LogicEngineFLDDefault, 1);
LogicEngineDeathStarRLD<> RLD(LogicEngineRLDDefault, 2);
LogicEngineControllerDefault controller(FLD, RLD);

HoloLights frontHP(10);
HoloLights rearHP(12);
HoloLights topHP(13);

NeoPixelPSI fpsi(3);
NeoPixelPSI rpsi(4);

I2CReceiver i2cReceiver(0x0a);
////////////////////////////////////////////////////////////////////////////////

void setup()
{

    REELTWO_READY();
    SetupEvent::ready();
    rpsi.set_color(1, 0, 255, 0);
    rpsi.set_color(2, 255, 255, 0);

}

void loop()
{
    AnimatedEvent::process();
}
