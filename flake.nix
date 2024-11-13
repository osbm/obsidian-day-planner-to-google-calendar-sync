{
  description = "Development Shell For this repository";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    # nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self , nixpkgs ,... }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
        inherit system;
    };
    environment_packages = with pkgs; [
      python312
      python312Packages.google-api-python-client
      python312Packages.google-auth-httplib2
      python312Packages.google-auth-oauthlib
    ];
  in {
    devShells."${system}".default = pkgs.mkShell {
      packages = environment_packages;
      shellHook = ''
        echo 'Welcome to the development environment of the Obsidian Day Planner to Google Calendar Sync repository. (definitely needs a shorter name)'
      '';
    };
    checks."${system}".default = pkgs.stdenvNoCC.mkDerivation {
        name = "unittest";
        dontBuild = true;
        src = ./.;
        doCheck = true;
        nativeBuildInputs = environment_packages;
        checkPhase = ''
          python -m unittest tests/main_test.py
        '';
        installPhase = ''
          mkdir -p "$out"
        '';
    };
  };
}
