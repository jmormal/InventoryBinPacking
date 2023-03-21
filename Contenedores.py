class Container():
    def __init__(self, id, Length, Width, Height):
        self.type=id
        self.Length=Length
        self.Width=Width
        self.Height=Height
        self.Volume=Length*Width*Height

    def SetAttributes(self, number_of_items, product_id,  weight=10):
        self.number_of_items=number_of_items
        self.weight=weight
        self.product_id=product_id