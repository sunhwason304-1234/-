# Tribal flame, left half in 0..100 x 0..160 (center x=50); mirrored for right half.
LEFT = [
 # big outer blade
 "M50 159 C38 140 15 122 13 94 C11 70 24 56 22 41 C21 29 13 16 3 3 C20 11 33 26 34 43 C35 60 25 74 26 94 C27 116 40 132 50 147 Z",
 # inner tall tongue
 "M49 76 C42 64 37 54 38 42 C39 32 36 22 28 11 C41 18 46 30 46 42 C46 52 48 60 50 68 Z",
 # small center tongue
 "M50 58 C46 51 45 45 47 38 C48 33 47 28 43 22 C50 26 53 33 51 42 Z",
 # middle flame with teardrop eye
 "M50 116 C39 111 30 102 30 89 C30 78 36 71 31 60 C42 65 47 75 47 87 C47 97 48 103 50 107 Z M35.5 93 C35.5 86 37.5 81 41 78 C42.5 84 42.5 91 40 97 C37.5 97.5 35.5 96 35.5 93 Z",
 # lower flame with teardrop eye
 "M50 144 C41 140 34 133 34 123 C34 115 38 110 35 102 C43 106 47 113 47 122 C47 130 48 134 50 137 Z M38.5 126 C38.5 121 40 117.5 42.5 115.5 C43.5 120 43.5 125 41.8 129 C40 129.3 38.5 128.3 38.5 126 Z",
 # side flick between blade and curls
 "M30 60 C33 52 36 48 41 46 C38 52 37 58 38 66 C36 64 33 62 30 60 Z",
]
SPINE = "M50 40 C53.5 80 54 120 50 160 C46 120 46.5 80 50 40 Z"
def flame(fill):
    l = "".join(f'<path d="{d}"/>' for d in LEFT)
    return f'<g fill="{fill}" fill-rule="evenodd">{l}<g transform="translate(100 0) scale(-1 1)">{l}</g><path d="{SPINE}"/></g>'
if __name__ == "__main__":
    open("flame.html","w").write(f'<html><body style="margin:0;background:#fff"><svg viewBox="-10 -5 120 170" width="480" height="680">{flame("#000")}</svg></body></html>')
