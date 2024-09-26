# constants.py

# Service URLs
UPSCALE_SERVICE_URL = "https://your-upscale-service-url.com/upscale"
RESIZE_WITH_BLEED_SERVICE_URL = "https://your-resize-service-url.com/resize_with_bleed"

# Default Values
DEFAULT_UPSCALE_FACTOR = 2
MIN_UPSCALE_FACTOR = 1
MAX_UPSCALE_FACTOR = 4

MIN_DIMENSION = 0
DEFAULT_BLEED_MARGIN = 10
MAX_BLEED_MARGIN = 2000

# Style File
STYLE_FILE = "styles.css"

FORMATS = {
    'A5-portrait': [[148, 210], [152, 214]],
    'A5-paysage': [[210, 148], [214, 152]],
    'A6-portrait': [[105, 148], [109, 152]],
    'A6-paysage': [[148, 105], [152, 109]],
    'A4-portrait': [[210, 297], [214, 301]],
    'A4-paysage': [[297, 210], [301, 214]],
    'A3-portrait': [[297, 420], [301, 424]],
    'A3-paysage': [[420, 297], [424, 301]],
    'A2-portrait': [[420, 594], [424, 598]],
    'A2-paysage': [[594, 420], [598, 424]],
    'A1-portrait': [[594, 841], [598, 845]],
    'A1-paysage': [[841, 594], [845, 598]],
    'A0-portrait': [[841, 1189], [845, 1193]],
    'A0-paysage': [[1189, 841], [1193, 845]],
    'B1-portrait': [[707, 1000], [711, 1004]],
    'B1-paysage': [[1000, 707], [1004, 711]],
    'B2-portrait': [[500, 707], [504, 711]],
    'B2-paysage': [[707, 500], [711, 504]],
    'carré': [[210, 210], [214, 214]],
    'carte de visite': [[54, 85], [58, 89]],
    'DL-portrait': [[99, 210], [103, 214]],
    'DL-paysage': [[210, 99], [214, 103]],
    'Etiquette': [[60, 60], [70, 70]],
    'carte de visite-portrait': [[54,85], [58, 89]],
    'carte de visite-paysage': [[85,54], [89, 58]],
    'Bookmarks-portrait': [[54,200], [58, 204]],
    'Bookmarks-paysage': [[200,54], [204, 58]],
}

# List of ratios
PROTRAIT_RATIOS = {
    "1:3": (1, 3),
    "1:2": (1, 2),
    "9:16": (9, 16),
    "10:16": (10, 16),
    "2:3": (2, 3),
    "3:4": (3, 4),
    "4:5": (4, 5),
}

LANDSCAPE_RATIOS = {
    "3:1": (3, 1),
    "2:1": (2, 1),
    "16:9": (16, 9),
    "16:10": (16, 10),
    "3:2": (3, 2),
    "4:3": (4, 3),
    "5:4": (5, 4),
}

# Define the styles and color palettes
styles = ["Auto", "General", "Realistic", "Design", "Render_3d", "Anime"]
palettes = ["Ember", "Fresh", "Jungle", "Magic", "Mosaic", "Pastel", "Ultramarine"]

# Define color swatches for each palette with 5 colors
palette_colors = {
    "Ember": ["#FF4500", "#FF8C00", "#FFD700", "#FF6347", "#FF7F50"],
    "Fresh": ["#00FA9A", "#7CFC00", "#ADFF2F", "#32CD32", "#98FB98"],
    "Jungle": ["#006400", "#228B22", "#32CD32", "#6B8E23", "#556B2F"],
    "Magic": ["#8A2BE2", "#9400D3", "#9932CC", "#BA55D3", "#DDA0DD"],
    "Mosaic": ["#FFD700", "#ADFF2F", "#00FFFF", "#FF69B4", "#1E90FF"],
    "Pastel": ["#FFB6C1", "#FFDAB9", "#E6E6FA", "#B0E0E6", "#FFFACD"],
    "Ultramarine": ["#4169E1", "#0000CD", "#000080", "#4682B4", "#5F9EA0"],
}
