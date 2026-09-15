from nutrition_management.food_knowledge.application.contracts import FoodFact


def import_food(repository, food: FoodFact) -> None:
    if not food.base_food_id:
        raise ValueError("base_food_id is required")
    repository.add_food(food)
