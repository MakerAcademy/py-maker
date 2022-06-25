
class LinearDecrease:
    def __init__(self, max_auction_time: float):
        self.max_auction_time = max_auction_time

    def price(self, initial_price: float, duration: float):
        if duration >= self.max_auction_time:
            return 0
        else:
            return initial_price * (self.max_auction_time - duration) / self.max_auction_time


class StairstepExponentialDecrease:
    def __init__(self, price_drop_time: float, multiplicative_factor: float):
        self.price_drop_time = price_drop_time
        self.multiplicative_factor = multiplicative_factor

    def price(self, initial_price: float, duration: float):
        number_of_price_drops = duration/self.price_drop_time
        factor = self.multiplicative_factor ** number_of_price_drops
        return initial_price * factor


class ExponentialDecrease:
    def __init__(self, multiplicative_factor: float):
        self.multiplicative_factor = multiplicative_factor

    def price(self, initial_price: float, duration: float):
        factor = self.multiplicative_factor ** duration
        return initial_price * factor
