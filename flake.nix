{
  description = "Render a glTF file to a WebM turntable video using Blender";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    gltf_to_png_py.url = "github:M4jor-Tom/gltf_to_png.py";
  };

  outputs = { self, nixpkgs, gltf_to_png_py }:
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
            START_ANGLE="0"
            ELEVATION="15"
            NUM_FRAMES="72"
            DURATION="3.0"
            while [ $# -gt 0 ]; do
              case "$1" in
                -i) INPUT="$2"; shift 2 ;;
                -o) OUTPUT="$2"; shift 2 ;;
                -r) REPORT="$2"; shift 2 ;;
                -a|--start-angle) START_ANGLE="$2"; shift 2 ;;
                -e|--elevation) ELEVATION="$2"; shift 2 ;;
                -n|--num-frames) NUM_FRAMES="$2"; shift 2 ;;
                -d|--duration) DURATION="$2"; shift 2 ;;
                *) echo "Unknown arg: $1"; exit 1 ;;
              esac
            done
            if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
              echo "Usage: gltf-to-webm -i <input.gltf> -o <output.webm> [options]"
              echo "Options:"
              echo "  -a, --start-angle <deg>   Starting camera angle (default: 0)"
              echo "  -e, --elevation <deg>     Camera elevation (default: 15)"
              echo "  -n, --num-frames <int>    Number of animation frames (default: 72)"
              echo "  -d, --duration <sec>      Output video duration (default: 3.0)"
              echo "  -r, --report <path>       Write JSON report"
              exit 1
            fi
            START="$(${pkgs.coreutils}/bin/date +%s)"
            export PATH="${pkgs.ffmpeg}/bin:$PATH"
            export GLTF_TO_PNG_RENDER="${gltf_to_png_py}/render.py"
            ${pkgs.blender}/bin/blender --background --python "${./render.py}" -- "$INPUT" "$OUTPUT" "$START_ANGLE" "$ELEVATION" "$NUM_FRAMES" "$DURATION"
            EXIT=$?
            ELAPSED="$(($(${pkgs.coreutils}/bin/date +%s) - START))"
            if [ -n "$REPORT" ]; then
              NAME="$(${pkgs.coreutils}/bin/basename "$OUTPUT" .webm)"
              echo "{\"success\":$([ $EXIT -eq 0 ] && echo true || echo false),\"model_name\":\"$NAME\",\"dimensions\":[512,512],\"duration\":$DURATION,\"codec\":\"vp9\",\"file\":\"$OUTPUT\",\"time_seconds\":$ELAPSED}" > "$REPORT"
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
