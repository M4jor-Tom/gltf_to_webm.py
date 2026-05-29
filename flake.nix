{
  description = "Render a glTF file to a WebM turntable video using Blender";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      forAllSystems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
    in
    {
      apps = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          script = pkgs.writeShellScriptBin "gltf-to-webm" ''
            set -eu
            INPUT=""
            OUTPUT=""
            REPORT=""
            while [ $# -gt 0 ]; do
              case "$1" in
                -i) INPUT="$2"; shift 2 ;;
                -o) OUTPUT="$2"; shift 2 ;;
                -r) REPORT="$2"; shift 2 ;;
                *) echo "Unknown arg: $1"; exit 1 ;;
              esac
            done
            if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
              echo "Usage: gltf-to-webm -i <input.gltf> -o <output.webm> [-r <report.json>]"
              exit 1
            fi
            START="$(${pkgs.coreutils}/bin/date +%s)"
            ${pkgs.blender}/bin/blender --background --python "${./render.py}" -- "$INPUT" "$OUTPUT"
            EXIT=$?
            ELAPSED="$(($(${pkgs.coreutils}/bin/date +%s) - START))"
            if [ -n "$REPORT" ]; then
              NAME="$(${pkgs.coreutils}/bin/basename "$OUTPUT" .webm)"
              echo "{\"success\":$([ $EXIT -eq 0 ] && echo true || echo false),\"model_name\":\"$NAME\",\"dimensions\":[512,512],\"duration\":3.0,\"codec\":\"vp9\",\"file\":\"$OUTPUT\",\"time_seconds\":$ELAPSED}" > "$REPORT"
            fi
            exit $EXIT
          '';
        in
        {
          default = {
            type = "app";
            program = "${script}/bin/gltf-to-webm";
          };
        }
      );
    };
}
