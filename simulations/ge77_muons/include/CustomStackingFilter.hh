#ifndef _CUSTOM_STACKING_FILTER_HH_
#define _CUSTOM_STACKING_FILTER_HH_

#include <optional>
#include <set>

#include "G4AnalysisManager.hh"
#include "G4GenericMessenger.hh"
#include "G4VUserEventInformation.hh"

#include "RMGIsotopeFilterScheme.hh"

class G4Event;
class CustomStackingFilter : public RMGIsotopeFilterScheme {

public:
  std::optional<G4ClassificationOfNewTrack> StackingActionClassify(const G4Track*, int stage) override;
};

#endif

// vim: tabstop=2 shiftwidth=2 expandtab
