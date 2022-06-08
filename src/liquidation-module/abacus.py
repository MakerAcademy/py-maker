
# these are done if RAY conversion isn't necessary
class LinearDecrease:
    def __init__(self, max_auction_time):
        self.max_auction_time = max_auction_time

    # RAY type conversion?

    def price(self, initial_price, duration):
        if duration >= self.max_auction_time:
            return 0
        else:
            return initial_price * (self.max_auction_time - duration) / self.max_auction_time


class StairstepExponentialDecrease:
    def __init__(self, price_drop_time, multiplicative_factor):
        self.price_drop_time = price_drop_time
        self.multiplicative_factor = multiplicative_factor

    def price(self, initial_price, duration):
        number_of_price_drops = duration/self.price_drop_time
        factor = self.multiplicative_factor ** number_of_price_drops
        return initial_price * factor


class ExponentialDecrease:
    def __init__(self, multiplicative_factor):
        self.multiplicative_factor = multiplicative_factor

    def price(self, initial_price, duration):
        factor = self.multiplicative_factor ** duration
        return initial_price * factor