
import colorsys
from argparse import ArgumentParser
from pathlib import Path


class ColorPalette:
    class Color:
        def __init__(self, r: int, g: int, b: int):
            self._r = r
            self._g = g
            self._b = b

        @property
        def as_tuple(self): return self._r, self._g, self._b
        @property
        def ansi_code(self): return f'\x1b[38;2;{self._r};{self._g};{self._b}m'
        @property
        def as_hex(self): return f'#{self._r:02x}{self._g:02x}{self._b:02x}'

    @staticmethod
    def from_hue(hue_degrees: int, num_colors: int, saturation_bounds: tuple[float, float],
                 lightness_bounds: tuple[float, float]):
        """
        Generate a sequence of colors with the same hue but varying saturation and lightness.

        :param hue_degrees: Hue in degrees (0-360)
        :param num_colors: Number of colors to generate
        :param saturation_bounds: Tuple of (min_saturation, max_saturation)
        :param lightness_bounds: Tuple of (min_lightness, max_lightness)
        :return: List of hex color codes
        """
        min_saturation, max_saturation = saturation_bounds
        min_lightness, max_lightness = lightness_bounds
        hue = hue_degrees / 360.0  # Convert hue to [0, 1] range
        colors = []
        # - Generate colors by varying saturation and lightness
        for i in range(num_colors):
            saturation = min_saturation + (max_saturation - min_saturation) * i / (num_colors - 1)
            lightness = min_lightness + (max_lightness - min_lightness) * i / (num_colors - 1)
            r, g, b = (int(v * 255) for v in colorsys.hls_to_rgb(hue, lightness, saturation))
            colors.append(ColorPalette.Color(r, g, b))
        return ColorPalette(colors)

    def __init__(self, colors: list[Color]):
        self._colors = colors

    @property
    def colors(self): return self._colors
    @property
    def as_format_dict(self): return {f'_{i + 1}': c.as_hex for i, c in enumerate(reversed(self._colors))}

    def print(self):
        for color in self._colors:
            print(color.ansi_code + color.as_hex + '\x1b[0m', end=' ')
        print()


if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a starship.toml file based on requirements.")
    parser.add_argument("hue", type=int, help="Hue value (0-360)")
    parser.add_argument("-t", "--template", type=Path, default=Path(__file__).parent / "starship_toml_template.txt",
                        help="Path to the starship.toml template file")
    parser.add_argument("-o", "--output-file", type=Path, default=Path(__file__).parent / "starship.toml",
                        help="Path to output the generated starship.toml file")
    parser.add_argument("-p", "--preview-only", action="store_true",
                        help="Print the generated color palette instead of writing to starship.toml")
    parser.add_argument("--saturation-bounds", type=float, nargs=2, default=(0.2, .9),
                        help="Min and max saturation values (0.0 to 1.0)")
    parser.add_argument("--lightness-bounds", type=float, nargs=2, default=(0.35, .95),
                        help="Min and max lightness values (0.0 to 1.0)")
    args = parser.parse_args()

    # - Generate color palette
    palette = ColorPalette.from_hue(args.hue, 6, tuple(args.saturation_bounds), tuple(args.lightness_bounds))

    # - Output results
    print("Generated color palette:")
    palette.print()

    # - Write to starship.toml if not in preview mode
    if not args.preview_only:
        with open(args.template, 'r', encoding='utf-8') as f:
            template = f.read()
        starship_toml_content = template.format(**palette.as_format_dict)
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(starship_toml_content)
        print(f"Generated starship.toml at {args.output_file}")
