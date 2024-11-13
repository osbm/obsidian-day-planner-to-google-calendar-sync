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
  in {
    devShells."${system}".default = pkgs.mkShell {
      # create an environment with nodejs_18, pnpm, and yarn
      packages = with pkgs; [
         (pkgs.python312.withPackages (ppkgs: [
            python312Packages.google-api-python-client
            python312Packages.google-auth-httplib2
            python312Packages.google-auth-oauthlib
          ]))
      ];

      shellHook = ''
        echo 'Welcome to the development environment of the Obsidian Day Planner to Google Calendar Sync repository. (definitely needs a shorter name)'
      '';
    };
    checks."${system}".default = pkgs.runCommandLocal "unittest" {
      src = ./.;
      nativeBuildInputs = with pkgs; [
         (pkgs.python312.withPackages (ppkgs: [
            python312Packages.google-api-python-client
            python312Packages.google-auth-httplib2
            python312Packages.google-auth-oauthlib
          ]))
      ];
    } ''
      python -m unittest tests/main_test.py
    '';

  };
}
