# constants.py

# Service URLs
UPSCALE_SERVICE_URL = "https://your-upscale-service-url.com/upscale"
RESIZE_WITH_BLEED_SERVICE_URL = "https://your-resize-service-url.com/resize_with_bleed"

# Default Values
DEFAULT_UPSCALE_FACTOR = 2
MIN_UPSCALE_FACTOR = 1
MAX_UPSCALE_FACTOR = 4

MIN_DIMENSION = 1
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