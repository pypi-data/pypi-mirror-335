from decimal import Decimal, getcontext
getcontext().prec = 10
class Color:
    def __init__(
            self, 
            name: str = "", 
            hex: str = "", 
            rgb: tuple = (-1, -1, -1),
            cmyk: tuple = (-1, -1, -1, -1)
        ):
        self.name = name
        self.hex = hex
        self.rgb = rgb
        self.cmyk = cmyk
    def get_rgb(
            self, 
            hex: str = "",
            cmyk: tuple = (-1, -1, -1, -1)
        ):
        hex = self.hex if hex == "" else hex
        cmyk = self.cmyk if cmyk == (-1, -1, -1, -1) else cmyk
        c, m, y, k = cmyk
        selector = "hex"
        if cmyk != (-1, -1, -1, -1):
            selector = "cmyk"
        if selector == "hex":
            if hex[0] == "#":
                hex = hex[1:]
            res = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            return res
        else:
            c, m, y, k = map(Decimal, (c, m, y, k))
            cs = c / 100
            ms = m / 100
            ys = y / 100
            ks = k / 100
            r = 255 * (1 - cs) * (1 - ks)
            g = 255 * (1 - ms) * (1 - ks)
            b = 255 * (1 - ys) * (1 - ks)
            r = round(r,2)
            g = round(g,2)
            b = round(b,2)
            res = (r, g, b)
            return res
    def get_hex(
            self, 
            rgb: tuple = (-1, -1, -1),
            cmyk: tuple = (-1, -1, -1, -1)
        ):
        cmyk = self.cmyk if cmyk == (-1, -1, -1, -1) else cmyk
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb   
        r, g, b = rgb
        if cmyk != (-1, -1, -1, -1):
            r, g, b = self.get_rgb(cmyk=cmyk)
        
        r = round(r)
        g = round(g)
        b = round(b)
        return ('{:02X}' * 3).format(r, g, b)
    def get_cmyk(
            self,
            rgb: tuple = (-1, -1, -1),
            hex: str = ""
    ):
        hex = self.hex if hex == "" else hex
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb
        r, g, b = rgb
        if hex:
            r, g, b = self.get_rgb(hex=hex)
        r, g, b = map(Decimal,(r, g, b))
        rs = r / 255
        gs = g / 255
        bs = b / 255
        k = 1 - max(rs, gs, bs)
        c = (1 - rs - k) / (1 - k)
        m = (1 - gs - k) / (1 - k)
        y = (1 - bs - k) / (1 - k)
        c, m, y, k = map(lambda x: round(x * 100, 4), (c, m, y, k))
        c = round(c, 2)
        m = round(m, 2)
        y = round(y, 2)
        k = round(k, 2)
        cmyk = (c, m, y, k)
        return cmyk