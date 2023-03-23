class Truck():
    def __init__(self, id, Length, Width, Height):
        self.id=id
        self.Length=Length
        self.Width=Width
        self.Height=Height
        self.Volume=Length*Width*Height
        self.weight=0