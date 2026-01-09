{ inputs, ... }:
{
  imports = [ inputs.devenv.flakeModule ];
  perSystem =
    { pkgs, ... }:
    {
      devenv.shells = {
        default = {
          languages.nix.enable = true;
          languages.python = {
            enable = true;
            directory = ./src;
          };
          git-hooks = {
            package = pkgs.prek;
            hooks = {
              nixfmt.enable = true;
              deadnix.enable = true;
              end-of-file-fixer.enable = true;
              flake-checker.enable = true;
            };
          };

          enterShell = ''
            echo "❄️ Started Steam Market devshell"
            tmuxinator local
          '';
        };
      };
    };
}
