#include "CustomStackingFilter.hh"

#include <set>

#include "G4Electron.hh"
#include "G4Event.hh"
#include "G4EventManager.hh"
#include "G4OpticalPhoton.hh"
#include "G4Positron.hh"
#include "G4RunManager.hh"

#include "RMGLog.hh"
#include "RMGOutputManager.hh"

namespace u = CLHEP;

// This stacks electrons and positrons into stage 1, which is only simulated if Ge77 was produced.
// The goal is to reduce Cerenkov light simulation for uninteresting events.
std::optional<G4ClassificationOfNewTrack> CustomStackingFilter::StackingActionClassify(
    const G4Track* aTrack,
    int stage
) {
  // hardcoded switch to turn it off. lol
  bool temporary_switch = true;
  // we are only interested in stacking into stage 1 after stage 0 finished.
  if (stage != 0) return std::nullopt;
  if (!temporary_switch) return std::nullopt;
  // defer tracking of electrons and positrons, as they are the main cause of cerenkov light.
  if (aTrack->GetDefinition() == G4Positron::PositronDefinition() ||
      aTrack->GetDefinition() == G4Electron::ElectronDefinition()) {
      
    // Check if the track is in the "tank" or "tank_water" volume
    auto* volume = aTrack->GetTouchableHandle()->GetVolume();
    if (volume) {
      auto volName = volume->GetName();
      // Make sure these match with whatever the name of these volumes are in your GDML
      if (volName == "tank" || volName == "tank_water" || volName == "outercryostat") {
        // electrons below 250 keV can not produce cerenkov light in water. And there is no way they pass
        // through the inner cryostat into the argon. So get rid of them.
        if(aTrack->GetKineticEnergy() < 250 * u::keV) {
          // This might be an issue for positrons due to annihilation, so we can only get rid of electrons.
          if (aTrack->GetDefinition() == G4Electron::ElectronDefinition()) {
            return fKill;
          }
          else {
            return std::nullopt; // Either simulate positrons directly or keep for later.
          }
        }
         // keep higher energy particles for later processing
         // The only issue here is that > 10 MeV electrons produced in the Water are deferred,
         // but they might produce electromagnetic showers that produce captures.
        return fWaiting;
      }
    }
    // Don't defer high energy electrons, as they might cause inelastic scattering and therefore nCaptures
    // low energy electrons will clutter the stack and possibly explode your RAM, so simulate them right away.
    if (aTrack->GetKineticEnergy() > 10 * u::MeV || aTrack->GetKineticEnergy() < 100 * u::keV) {
      return std::nullopt;
    }
    return fWaiting;
  }
  return std::nullopt;
}

// vim: tabstop=2 shiftwidth=2 expandtab
