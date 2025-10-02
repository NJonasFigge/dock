
import colorsys
from argparse import ArgumentParser
from pathlib import Path


class ColorPalette:
    ANSI_RESET = '\x1b[0m'

    class Color:
        def __init__(self, r: int, g: int, b: int):
            self._r = r
            self._g = g
            self._b = b

        @property
        def as_tuple(self): return self._r, self._g, self._b
        @property
        def ansi_code_fg(self): return f'\x1b[38;2;{self._r};{self._g};{self._b}m'
        @property
        def ansi_code_bg(self): return f'\x1b[48;2;{self._r};{self._g};{self._b}m'
        @property
        def as_hex(self): return f'#{self._r:02x}{self._g:02x}{self._b:02x}'

    @staticmethod
    def from_hue(hue_degrees: int, num_colors: int, spacers: list[int], saturation_bounds: tuple[float, float],
                 lightness_bounds: tuple[float, float]):
        """
        Generate a sequence of colors with the same hue but varying saturation and lightness.

        :param hue_degrees: Hue in degrees (0-360)
        :param num_colors: Number of colors to generate
        :param spacers: List of indices to use as spacers (these colors will be generated but not used, negative
            indices allowed)
        :param saturation_bounds: Tuple of (min_saturation, max_saturation)
        :param lightness_bounds: Tuple of (min_lightness, max_lightness)
        :return: List of hex color codes
        """
        min_saturation, max_saturation = saturation_bounds
        min_lightness, max_lightness = lightness_bounds
        hue = hue_degrees / 360.0  # Convert hue to [0, 1] range
        colors = []
        total_num_colors = num_colors + len(spacers)
        # - Generate colors by varying saturation and lightness
        for i in range(total_num_colors):
            saturation = min_saturation + (max_saturation - min_saturation) * i / (total_num_colors - 1)
            lightness = min_lightness + (max_lightness - min_lightness) * i / (total_num_colors - 1)
            r, g, b = (int(v * 255) for v in colorsys.hls_to_rgb(hue, lightness, saturation))
            colors.append(ColorPalette.Color(r, g, b))
        return ColorPalette(colors, thereof_spacers=spacers)

    def __init__(self, colors: list[Color], thereof_spacers: list[int]):
        """
        Instantiate a ColorPalette.
        :param colors: List of Color objects
        :param thereof_spacers: List of indices to use as spacers (these colors will be generated but not used,
            negative indices allowed)
        """
        self._colors = colors
        self._spacers = [s if s >= 0 else len(self._colors) + s for s in thereof_spacers]

    @property
    def as_format_dict(self):
        usable_colors = [c for i, c in enumerate(self._colors) if i not in self._spacers]
        return {f'c{i}': color.as_hex for i, color in enumerate(usable_colors)}

    def print_color_codes(self):
        for color in self._colors:
            print(color.ansi_code_fg + color.as_hex + '\x1b[0m', end=' ')
        print()

    def print_table(self):
        digits = len(str(len(self._colors)))
        for i, fg_color in enumerate(self._colors):
            for j, bg_color in enumerate(self._colors):
                text = f' {str(i + 1).rjust(digits)} on {str(j + 1).rjust(digits)} '
                if i in self._spacers or j in self._spacers:
                    print(' ' * len(text), end=' ')
                else:
                    print(f'{bg_color.ansi_code_bg}{fg_color.ansi_code_fg}{text}{self.ANSI_RESET}', end=' ')
            print()

    def print_preview(self):
        usable_colors = [c for i, c in enumerate(self._colors) if i not in self._spacers]
        set_colors = lambda i, j: usable_colors[i].ansi_code_fg + usable_colors[j].ansi_code_bg
        print(f'{usable_colors[6].ansi_code_fg}░▒▓'
              f'{set_colors(0, 6)}  '
              f'{set_colors(6, 5)}▄'
              f'{set_colors(0, 5)} user@host '
              f'{set_colors(5, 4)}▄'
              f'{set_colors(0, 4)} ~/dock/system-setup '
              f'{set_colors(4, 3)}▄'
              f'{set_colors(5, 3)}  main ? '
              f'{set_colors(3, 2)}▄'
              f'{set_colors(5, 2)} venv '
              f'{set_colors(2, 1)}▄'
              f'{set_colors(5, 1)}  13:49 '
              f'{set_colors(1, 0)}▄'
              f'{set_colors(5, 0)} took 3s '
              f'{self.ANSI_RESET}{usable_colors[0].ansi_code_fg}▄'
              f'{self.ANSI_RESET}')


if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a starship.toml file based on requirements.")
    parser.add_argument("hue", type=int, help="Hue value (0-360)")
    parser.add_argument("-t", "--template", type=Path, default=Path(__file__).parent / "starship_template.toml",
                        help="Path to the starship.toml template file")
    parser.add_argument("-o", "--output-file", type=Path, default=Path(__file__).parent / "starship.toml",
                        help="Path to output the generated starship.toml file")
    parser.add_argument("-p", "--preview", action="store_true",
                        help="Print the generated color palette instead of writing to starship.toml")
    parser.add_argument("--good-spacers", action="store_true",
                        help="Use a predefined set of good spacer indices. Currently: 4 5 6 7 9 -3 -2")
    parser.add_argument("--spacers", type=int, nargs='*',
                        help="Indices of colors to use as spacers. E.g., --spacer 2 5 means 2 more colors are "
                             "generated at index 2 and 5, but they will not be used. "
                             "(Overrides --good-spacers if set.)")
    parser.add_argument("--saturation-bounds", type=float, nargs=2, default=(0.1, .6),
                        help="Min and max saturation values (0.0 to 1.0)")
    parser.add_argument("--lightness-bounds", type=float, nargs=2, default=(0.22, .95),
                        help="Min and max lightness values (0.0 to 1.0)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output except for errors")
    args = parser.parse_args()

    if args.spacers is None:
        if args.good_spacers:
            args.spacers = [4, 5, 6, 7, 9, -3, -2]
        else:
            args.spacers = []

    # - Generate color palette
    palette = ColorPalette.from_hue(args.hue, num_colors=7, spacers=args.spacers,
                                    saturation_bounds=args.saturation_bounds,
                                    lightness_bounds=args.lightness_bounds)

    # - Output results
    if not args.quiet:
        print("Generated color palette:")
        palette.print_color_codes()
        print("Color table:")
        palette.print_table()
        print("This will look something like this in your terminal:")
        palette.print_preview()

    if not args.preview:
        # - Read template
        with open(args.template, 'r', encoding='utf-8') as f:
            template = f.read()
        # - Escape curly braces for str.format()
        template = template.replace('{', '&curlyopen').replace('}', '%curlyclose')
        # - Replace '%<' and '>%' with '{' and '}' for str.format()
        template = template.replace('%<', '{').replace('>%', '}')
        # - Prepare substitutions
        substitutions = palette.as_format_dict
        substitutions['user_cmd'] = str(Path(__file__).parent / 'beautiful_user.sh')
        # - Format template
        starship_toml_content = template.format(**substitutions)
        # - Un-escape curly braces
        starship_toml_content = starship_toml_content.replace('&curlyopen', '{').replace('%curlyclose', '}')
        # - Write to file
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(starship_toml_content)
        print(f"Generated starship.toml at {args.output_file}")
