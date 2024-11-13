{
  description = "Development Shell For this repository";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self , nixpkgs ,... }: let
    system = "x86_64-linux";
  in {
    devShells."${system}".default = let
      pkgs = import nixpkgs {
        inherit system;
      };
    in pkgs.mkShell {
      # create an environment with nodejs_18, pnpm, and yarn
      packages = with pkgs; [
         (pkgs.python312.withPackages (ppkgs: [
            python312Packages.pytest
            python312Packages.google-api-python-client
            python312Packages.google-auth-httplib2
            python312Packages.google-auth-oauthlib
          ]))
      ];

      shellHook = ''
        echo Welcommeeeee
      '';
    };
  };
}