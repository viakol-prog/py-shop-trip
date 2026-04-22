import json
import datetime
from .utils import get_distance
from typing import Any, Union


class Car:
    def __init__(self, brand: str, fuel_consumption: float) -> None:
        self.brand = brand
        self.fuel_consumption = fuel_consumption

    def fuel_needed(self, distance: float) -> float:
        return (distance * self.fuel_consumption) / 100


class Shop:
    def __init__(
            self,
            name: str,
            location: list | tuple,
            products: list
    ) -> None:
        self.name = name
        self.location = list(location)
        self.products = products


class Customer:
    def __init__(
            self,
            name: str,
            location: Union[list, tuple],
            money: Union[int, float],
            product_cart: dict,
            car: Any
    ) -> None:
        self.name = name
        self.location = list(location)
        self.money = money
        self.product_cart = product_cart
        self.car = car
        self.initial_location = list(location)

    def ride_to(self, shop: "Shop") -> None:
        print(f"{self.name} rides to {shop.name}")
        self.location = shop.location.copy()

    def go_home(self) -> None:
        print(f"{self.name} rides home")
        self.location = self.initial_location.copy()

    def calculate_trip_cost(
            self,
            shop: "Shop",
            fuel_price: float
    ) -> float | None:
        for prod in self.product_cart:
            if prod not in shop.products:
                return None

        products_cost = 0
        for prod, qty in self.product_cart.items():
            products_cost += shop.products[prod] * qty
        distance_to = get_distance(self.initial_location, shop.location)
        fuel_to = self.car.fuel_needed(distance_to)
        distance_back = get_distance(shop.location, self.initial_location)
        fuel_back = self.car.fuel_needed(distance_back)
        total_fuel = fuel_to + fuel_back
        fuel_cost = total_fuel * fuel_price
        total_cost = round(products_cost + fuel_cost, 2)
        fuel_cost = round(fuel_cost, 2)
        return products_cost, fuel_cost, total_cost

    def print_receipt(self, shop: str, products_cost: float) -> None:
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print()
        print(f"Date: {now}")
        print(f"Thanks, {self.name}, for your purchase!")
        print("You have bought:")
        for prod, qty in self.product_cart.items():
            price = shop.products[prod] * qty
            if float(price).is_integer():
                price_str = str(int(price))
            else:
                price_str = f"{price:g}"
            suffix = "s" if qty > 1 else ""
            print(f"{qty} {prod}{suffix} for {price_str} dollars")
        print(f"Total cost is {products_cost:g} dollars")
        print("See you again!")
        print()

    def perform_trip(
            self,
            shop: str,
            products_cost: float,
            fuel_cost: float
    ) -> None:
        total_cost = products_cost + fuel_cost
        self.ride_to(shop)
        self.print_receipt(shop, products_cost)
        self.money -= total_cost
        self.go_home()
        self.money = round(self.money, 2)
        print(f"{self.name} now has {self.money:g} dollars")
        print()


def shop_trip() -> None:
    with open("config.json", "r") as f:
        data = json.load(f)
    fuel_price = data.get("FUEL_PRICE", 50.0)
    shops = [Shop(s["name"], s["location"], s["products"])
             for s in data["shops"]]
    for c_data in data["customers"]:
        car = Car(c_data["car"]["brand"], c_data["car"]["fuel_consumption"])
        customer = Customer(
            c_data["name"],
            c_data["location"],
            c_data["money"],
            c_data["product_cart"],
            car
        )
        print(f"{customer.name} has {customer.money} dollars")
        valid_trips = []
        for shop in shops:
            result = customer.calculate_trip_cost(shop, fuel_price)
            if result is not None:
                products_cost, fuel_cost, total_cost = result
                print(f"{customer.name}'s trip to the "
                      f"{shop.name} costs {total_cost}")
                if total_cost <= customer.money:
                    valid_trips.append((total_cost, products_cost,
                                        fuel_cost, shop))
        if valid_trips:
            best = min(valid_trips, key=lambda x: x[0])
            customer.perform_trip(best[3], best[1], best[2])
        else:
            print(f"{customer.name} doesn't have enough money "
                  f"to make a purchase in any shop")


if __name__ == "__main__":
    shop_trip()
