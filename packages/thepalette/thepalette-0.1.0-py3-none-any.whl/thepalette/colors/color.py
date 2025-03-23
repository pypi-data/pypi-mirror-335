from decimal import Decimal, getcontext
getcontext().prec = 10
class Color:
    def __init__(
            self, 
            name: str = "", 
            hex: str = "", 
            rgb: tuple = (-1, -1, -1),
            cmyk: tuple = (-1, -1, -1, -1),
            hsv: tuple = (-1, -1, -1),
            hsl: tuple = (-1, -1, -1)
        ):
        self.name = name
        self.hex = hex
        self.rgb = rgb
        self.cmyk = cmyk
        self.hsv = hsv
        self.hsl = hsl
    def get_rgb(
            self, 
            hex: str = "",
            cmyk: tuple = (-1, -1, -1, -1),
            hsv: tuple = (-1, -1, -1),
            hsl: tuple = (-1, -1, -1)
        ):
        hex = self.hex if hex == "" else hex
        cmyk = self.cmyk if cmyk == (-1, -1, -1, -1) else cmyk
        hsv = self.hsv if hsv == (-1, -1, -1) else hsv
        hsl = self.hsl if hsl == (-1, -1, -1) else hsl
        if self.rgb != (-1, -1, -1):
            return self.rgb
        elif cmyk != (-1, -1, -1, -1):
            c, m, y, k = map(Decimal, cmyk)
            cs = c / 100
            ms = m / 100
            ys = y / 100
            ks = k / 100
            r = 255 * (1 - cs) * (1 - ks)
            g = 255 * (1 - ms) * (1 - ks)
            b = 255 * (1 - ys) * (1 - ks)
            r = round(r, 3)
            g = round(g, 3)
            b = round(b, 3)
            res = (r, g, b)
            return res
        elif hsv != (-1, -1, -1):
            h, s, v = hsv
            s /= 100
            v /= 100
            h, s, v = map(Decimal, (h, s, v))
            c = v * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = v - c
            rs, gs, bs = 0, 0, 0
            if 0 <= h < 60:
                rs, gs, bs = c, x, 0
            elif 60 <= h < 120:
                rs, gs, bs = x, c, 0
            elif 120 <= h < 180:
                rs, gs, bs = 0, c, x
            elif 180 <= h < 240:
                rs, gs, bs = 0, x, c
            elif 240 <= h < 300:
                rs, gs, bs = x, 0, c
            elif 300 <= h <= 360:
                rs, gs, bs = c, 0, x
            r, g, b = (rs + m) * 255, (gs + m) * 255, (bs + m) * 255
            return (r, g, b)
        elif hsl != (-1, -1, -1):
            h, s, l = hsl
            s /= 100
            l /= 100
            h, s, l = map(Decimal, (h, s, l))
            c = (1 - abs(2 * l - 1)) * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = l - c / 2
            rs, gs, bs = 0, 0, 0
            if 0 <= h < 60:
                rs, gs, bs = c, x, 0
            elif 60 <= h < 120:
                rs, gs, bs = x, c, 0
            elif 120 <= h < 180:
                rs, gs, bs = 0, c, x
            elif 180 <= h < 240:
                rs, gs, bs = 0, x, c
            elif 240 <= h < 300:
                rs, gs, bs = x, 0, c
            elif 300 <= h < 360:
                rs, gs, bs = c, 0, x
            r, g, b = (rs + m) * 255, (gs + m) * 255, (bs + m) * 255
            return (r, g, b)
        else:
            if hex[0] == "#":
                hex = hex[1:]
            res = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            return res
    def get_hex(
            self, 
            rgb: tuple = (-1, -1, -1),
            cmyk: tuple = (-1, -1, -1, -1),
            hsv: tuple = (-1, -1, -1),
            hsl: tuple = (-1, -1, -1)
        ):
        cmyk = self.cmyk if cmyk == (-1, -1, -1, -1) else cmyk
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb   
        hsv = self.hsv if hsv == (-1, -1, -1) else hsv
        hsl = self.hsl if hsl == (-1, -1, -1) else hsl
        r, g, b = rgb
        if cmyk != (-1, -1, -1, -1):
            r, g, b = self.get_rgb(cmyk=cmyk)
        elif hsv != (-1, -1, -1):
            r, g, b = self.get_rgb(hsv=hsv)
        elif hsl != (-1, -1, -1):
            r, g, b = self.get_rgb(hsl=hsl)
        r = round(r)
        g = round(g)
        b = round(b)
        return ('{:02X}' * 3).format(r, g, b)
    def get_cmyk(
            self,
            rgb: tuple = (-1, -1, -1),
            hex: str = "",
            hsv: tuple = (-1, -1, -1),
            hsl: tuple = (-1, -1, -1)
    ):
        hex = self.hex if hex == "" else hex
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb
        hsv = self.hsv if hsv == (-1, -1, -1) else hsv
        hsl = self.hsl if hsl == (-1, -1, -1) else hsl
        r, g, b = rgb
        if hex:
            r, g, b = self.get_rgb(hex=hex)
        elif hsv != (-1, -1, -1):
            r, g, b = self.get_rgb(hsv=hsv)
        elif hsl != (-1, -1, -1):
            r, g, b = self.get_rgb(hsl=hsl)
        r, g, b = map(Decimal,(r, g, b))
        rs = r / 255
        gs = g / 255
        bs = b / 255
        k = 1 - max(rs, gs, bs)
        if k == 1:
            return (0, 0, 0, 100)
        c = (1 - rs - k) / (1 - k)
        m = (1 - gs - k) / (1 - k)
        y = (1 - bs - k) / (1 - k)
        c, m, y, k = map(lambda x: round(x * 100, 4), (c, m, y, k))
        c = round(c, 3)
        m = round(m, 3)
        y = round(y, 3)
        k = round(k, 3)
        cmyk = (c, m, y, k)
        return cmyk
    def get_hsv(
            self,
            rgb: tuple = (-1, -1, -1),
            hex: str = "",
            cmyk: tuple = (-1, -1, -1, -1),
            hsl: tuple = (-1, -1, -1)
            
    ):
        hex = self.hex if hex == "" else hex
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb
        cmyk = self.cmyk if cmyk == (-1, -1, -1, -1) else cmyk
        hsl = self.hsl if hsl == (-1, -1, -1) else hsl
        r, g, b = rgb
        if hex:
            r, g, b = self.get_rgb(hex=hex)
        elif cmyk != (-1, -1, -1, -1):
            r, g, b = self.get_rgb(cmyk=cmyk)
        elif hsl != (-1, -1, -1):
            r, g, b = self.get_rgb(hsl=hsl)
        r, g, b = map(Decimal,(r, g, b))
        rs = r / 255
        gs = g / 255
        bs = b / 255
        cmax = max(rs, gs, bs)
        cmin = min(rs, gs, bs)
        delta = cmax - cmin
        v = cmax
        if cmax == 0:
            s = 0
        else:
            s = delta / cmax
        if cmax == rs:
            h = (gs - bs) / delta
        elif cmax == gs:
            h = 2 + (bs - rs) / delta
        elif cmax == bs:
            h = 4 + (rs - gs) / delta
        h *= 60
        if h < 0:
            h += 360
        h = round(h, 3)
        s = round(s * 100, 3)
        v = round(v * 100, 3)
        return (h, s, v)
    def get_hsl(
            self,
            rgb: tuple = (-1, -1, -1),
            hex: str = "",
            cmyk: tuple = (-1, -1, -1, -1),
            hsv: tuple = (-1, -1, -1)
    ):
        hex = self.hex if hex == "" else hex
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb
        cmyk = self.cmyk if cmyk == (-1, -1, -1, -1) else cmyk
        hsv = self.hsv if hsv == (-1, -1, -1) else hsv
        r, g, b = rgb
        if hex:
            r, g, b = self.get_rgb(hex=hex)
        elif cmyk != (-1, -1, -1, -1):
            r, g, b = self.get_rgb(cmyk=cmyk)
        elif hsv != (-1, -1, -1):
            r, g, b = self.get_rgb(hsv=hsv)
        r, g, b = map(Decimal,(r, g, b))
        rs = r / 255
        gs = g / 255
        bs = b / 255
        cmax = max(rs, gs, bs)
        cmin = min(rs, gs, bs)
        delta = cmax - cmin
        l = (cmax + cmin) / 2
        if delta == 0:
            s = 0
        else:
            s = delta / (1 - abs(2 * l - 1))
        if delta == 0:
            h = 0
        elif cmax == rs:
            h = (gs - bs) / delta
        elif cmax == gs:
            h = 2 + (bs - rs) / delta
        elif cmax == bs:
            h = 4 + (rs - gs) / delta
        h *= 60
        if h < 0:
            h += 360
        h = round(h, 3)
        s = round(s * 100, 3)
        l = round(l * 100, 3)
        return (h, s, l)
clr1 = Color(hex="#3F7D58")
clr2 = Color(rgb= (155, 202, 34))
clr3 = Color(cmyk=(66, 10, 93, 39))
clr4 = Color(hsv=(110, 70, 79))

clr5 = Color(hex="#A0C878")
clr6 = Color(rgb=(177, 218, 111))
clr7 = Color(cmyk=(27, 13, 60, 96))
clr8 = Color(hsl=(80, 50, 85))

clr9 = Color(hex="#98D2C0")
clr10 = Color(rgb=(166, 219, 197))
clr11 = Color(hsv=(111, 40, 51))
clr12 = Color(hsl=(169, 50, 74))

clr13 = Color(hex="#FFCF50")
clr14 = Color(cmyk=(99, 24, 5, 17))
clr15 = Color(hsv=(45, 99, 100))
clr16 = Color(hsl=(234, 81, 29))

clr17 = Color(rgb=(189, 19, 211))
clr18 = Color(cmyk=(0, 91, 10, 0))
clr19 = Color(hsv=(300, 91, 72))
clr20 = Color(hsl=(300, 81, 41))


print(clr1.get_hsl())
print(clr2.get_hsl())
print(clr3.get_hsl())
print(clr4.get_hsl())

print(clr5.get_hsv())
print(clr6.get_hsv())
print(clr7.get_hsv())
print(clr8.get_hsv())

print(clr9.get_cmyk())
print(clr10.get_cmyk())
print(clr11.get_cmyk())
print(clr12.get_cmyk())

print(clr13.get_rgb())
print(clr14.get_rgb())
print(clr15.get_rgb())
print(clr16.get_rgb())

print(clr17.get_hex())
print(clr18.get_hex())
print(clr19.get_hex())
print(clr20.get_hex())