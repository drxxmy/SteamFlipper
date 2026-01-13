{ inputs, ... }:
{
  imports = [ inputs.devenv.flakeModule ];
  perSystem =
    { pkgs, ... }:
    {
      devenv.shells = {
        default = {
          packages = with pkgs; [
            pnpm
            nodejs
          ];
          languages.nix.enable = true;
          languages.python = {
            enable = true;
            directory = "./backend/src";
            uv = {
              enable = true;
              sync.enable = true;
            };
            venv.enable = true;
          };
          git-hooks = {
            package = pkgs.prek;
            hooks = {
              nixfmt.enable = true;
              deadnix.enable = true;
              end-of-file-fixer.enable = true;
              flake-checker.enable = true;
              black.enable = true;
            };
          };

          processes = {
            fastapi = {
              cwd = "./backend/src";
              exec = "uvicorn app.main:app --reload";
            };
            steamflipper = {
              cwd = "./backend/src";
              exec = "python main.py";
            };
            vue-website = {
              cwd = "./frontend/src";
              exec = "pnpm run dev";
            };
          };

          enterShell = ''
            echo "❄️ Started Steam Market devshell"
          '';
        };
      };
    };
}
