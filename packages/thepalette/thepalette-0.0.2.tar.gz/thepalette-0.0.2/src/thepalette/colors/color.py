class Color:
    def __init__(
            self, 
            name: str = "", 
            hex: str = "", 
            rgb: tuple = (0, 0, 0)
        ):
        self.name = name
        self.hex = hex
        self.rgb = rgb
    def get_rgb(
            self, 
            hex: str = ""
        ):
        hex = self.hex if hex == "" else hex
        if hex[0] == "#":
            hex = hex[1:]
        res = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        return res
    def get_hex(
            self, 
            rgb: tuple = (-1, -1, -1)):
        rgb = self.rgb if rgb == (-1, -1, -1) else rgb   
        r, g, b = rgb
        return ('{:02X}' * 3).format(r, g, b)