{
  description = "parselglossy";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pypi-deps-db = {
      url = "github:DavHau/pypi-deps-db";
      flake = false;
    };
    mach-nix = {
      url = "mach-nix/3.5.0";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
      inputs.pypi-deps-db.follows = "pypi-deps-db";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pypi-deps-db, mach-nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = mach-nix.lib."${system}".mkPython {
          requirements = ''
            click
            pyparsing~=3.0
            pyyaml
            networkx
            coverage
            #hypothesis
            #pre-commit
            pytest
            #pytest-black
            #pytest-cov
            #pytest-flake8
            #pytest-mypy
            #pytest-sugar
            #black==22.3.0  # NOTE We pin black to avoid inconsistent formatting (and failing CI)
            #flake8
            #mypy
            #jupyterlab
            flit_core
          '';
        };
      in
      {
        devShell = pkgs.mkShell {
          nativeBuildInputs = with pkgs; [
            pythonEnv
          ];
        };
      });
}
