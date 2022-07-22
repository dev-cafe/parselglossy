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
      url = "mach-nix/3.4.0";
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
            hypothesis
            pre-commit
            pytest
            pytest-black
            pytest-cov
            pytest-flake8
            pytest-mypy
            pytest-sugar
            black==22.3.0  # NOTE We pin black to avoid inconsistent formatting (and failing CI)
            flake8
            mypy
            jupyterlab
            flit_core
          '' + builtins.readFile ./docs/requirements.txt;
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
