{
    description = "PortesObertes";

    inputs = {
        nixpkgs.url     = "github:NixOS/nixpkgs/nixos-24.11";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils, ... }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs { inherit system; };

                python = with pkgs; [ python312Full ];

                dependencies = with pkgs.python312Packages; [
                    fastapi
                    sqlmodel
                    pydantic
                    pyserial
                    requests
                    bcrypt
                ];

                dev_tools = with pkgs.python312Packages; [
                    bandit
                    autopep8
                ];

            in {
                devShells.default = pkgs.mkShell {
                    buildInputs = python ++ dependencies ++ dev_tools;
                };
            }
        );
}
