#include "RMGHardware.hh"
#include "RMGManager.hh"

#include "CosmogenicPhysics.hh"
#include "CustomStackingFilter.hh"

#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

#include "CLI11.hpp"

int main(int argc, char **argv) {
  CLI::App app{"Cosmogenic Simulations"};

  int nthreads = 16;
  std::string macroName;
  std::string filename;
  std::string outputfilename = "build/out.hdf5";

  app.add_option("-m,--macro", macroName,
                 "<Geant4 macro filename> Default: None");
  app.add_option("-g,--gdml", filename,
                  "<GDML filename> Default: None");
  app.add_option("-t, --nthreads", nthreads,
                 "<number of threads to use> Default: 16");
  app.add_option("-o,--output", outputfilename,
                 "<output filename> Default: build/out.hdf5>");
  CLI11_PARSE(app, argc, argv);

  RMGManager manager("FullCosmogenics", argc, argv);
  std::cout << "current gdml file: " << filename << std::endl;
  manager.GetDetectorConstruction()->IncludeGDMLFile(filename);

  // Custom User init
  auto user_init = manager.GetUserInit();
  // This is to apply custom stackingAction to speed up the simulation
  user_init->AddOptionalOutputScheme<CustomStackingFilter>(
        "CustomStackingFilter");

  // Dont ask why but this is here to avoid a segfault
  auto *RunManager = manager.GetG4RunManager();
  RunManager->SetNumberOfThreads(nthreads);
  // Overwrite RMGPhysics to use own Optical Processes.
  // We disable scintillation light cause otherwise this would take eons to simulate.
  // We also disable cerenkov light for muons as that would massively slow down the simulation.
  manager.SetUserInit(new CosmogenicPhysics());

  
  // Interactive or batch mode?
  if (!macroName.empty())
    manager.IncludeMacroFile(macroName);
  else
    manager.SetInteractive(true);

  // Outputfilename and Threads. Then run
  
  manager.GetOutputManager()->SetOutputFileName(outputfilename);
  manager.SetNumberOfThreads(nthreads);
  manager.GetOutputManager()->SetOutputOverwriteFiles(true);
  manager.Initialize();
  manager.Run();

  return 0;
}
// vim: tabstop=2 shiftwidth=2 expandtab
