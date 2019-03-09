#define USE_DEBUG
#include "ReelTwo.h"
#include "dome/Logics.h"
#include "dome/HoloLights.h"
#include "dome/LogicEngineController.h"
#include "dome/PSIMatrix.h"
#include "i2c/I2CReceiver.h"

LogicEngineDeathStarFLD<> FLD(1, LogicEngineFLDDefault);
LogicEngineDeathStarRLD<> RLD(2, LogicEngineRLDDefault);
LogicEngineControllerDefault controller(FLD, RLD);

HoloLights frontHP(10, 10);
HoloLights rearHP(12, 12);
HoloLights topHP(13, 13);

PSIMatrix rearPSI(22,23,2);
PSIMatrix frontPSI(24,25,1);

I2CReceiver i2cReceiver(0x0a);
////////////////////////////////////////////////////////////////////////////////

void setup()
{
    REELTWO_READY();
    SetupEvent::ready();

}

void loop()
{
    AnimatedEvent::process();
}
