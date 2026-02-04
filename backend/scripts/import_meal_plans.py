"""
Meal Plan Import Script v2

Parses meal plan PDF text files and imports them into the database.
Run from the backend directory:
    cd /Users/stephanketterer/sloth/backend
    source venv/bin/activate
    python scripts/import_meal_plans.py
"""

import re
import sys
import os

# Add the parent directory to path so we can import our app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.meal_plan import MealPlan, Meal, Ingredient
from app.models.user import Gender


def parse_meal_plan_file(filepath: str, gender: str) -> list[dict]:
    """Parse a meal plan text file and return structured data."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    meal_plans = []

    # Split by "Level X Tag Y" headers
    day_pattern = r'Level\s+(\d)\s+Tag\s+(\d+)'
    headers = list(re.finditer(day_pattern, content))

    for i, match in enumerate(headers):
        level = int(match.group(1))
        day_number = int(match.group(2))

        # Get the content between this header and the next (or end of file)
        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        day_content = content[start:end]

        # Parse daily totals from "Gesamt: XXXg P XXXg KH XXXg F XXXX kcal"
        gesamt_pattern = r'Gesamt:\s*(\d+)g\s*P\s*(\d+)g\s*KH\s*(\d+)g\s*F\s*(\d+)\s*kcal'
        gesamt_match = re.search(gesamt_pattern, day_content)

        if gesamt_match:
            total_protein = int(gesamt_match.group(1))
            total_carbs = int(gesamt_match.group(2))
            total_fat = int(gesamt_match.group(3))
            total_kcal = int(gesamt_match.group(4))
        else:
            print(f"Warning: Could not parse totals for Level {level} Tag {day_number}")
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            total_kcal = 0

        # Parse meals
        meals = parse_meals_v2(day_content)

        meal_plan = {
            'level': level,
            'day_number': day_number,
            'gender': gender,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'total_kcal': total_kcal,
            'meals': meals,
            'name': f"Tag {day_number}",
            'description': f"Stufe {level} - Tag {day_number}"
        }

        meal_plans.append(meal_plan)
        print(f"Parsed: Level {level} Tag {day_number} ({gender}) - {total_kcal} kcal, {len(meals)} meals")

    return meal_plans


def parse_meals_v2(day_content: str) -> list[dict]:
    """
    Parse individual meals from day content.

    The structure is:
    - Meal label on its own line (Frühstück, Miattgessen, Abendessen, Snacks)
    - Ingredients listed BELOW the label with macros on the right
    - Macros appear as: XXg P, XXg KH, XXg F, XXX kcal
    """
    meals = []

    # Meal type mappings
    meal_types = {
        'Frühstück': 'breakfast',
        'Miattgessen': 'lunch',  # Typo in PDF
        'Mittagessen': 'lunch',
        'Abendessen': 'dinner',
        'Snacks': 'snack',
        'Snack': 'snack'
    }

    # Split content into lines
    lines = day_content.split('\n')

    # Find meal section boundaries
    meal_sections = []  # [(start_line, meal_type), ...]

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped in meal_types:
            meal_sections.append((i, meal_types[stripped]))

    # Process each meal section
    for idx, (start_line, meal_type) in enumerate(meal_sections):
        # Determine end line (next meal section or "Gesamt:" or end)
        if idx + 1 < len(meal_sections):
            end_line = meal_sections[idx + 1][0]
        else:
            # Find "Gesamt:" line
            end_line = len(lines)
            for i in range(start_line, len(lines)):
                if 'Gesamt:' in lines[i]:
                    end_line = i
                    break

        # Extract section content (lines between this meal label and next)
        section_lines = lines[start_line + 1:end_line]
        section_content = '\n'.join(section_lines)

        # Parse macros for this meal
        protein, carbs, fat, kcal = parse_meal_macros(section_content)

        # Parse ingredients
        ingredients = parse_ingredients_from_section(section_lines)

        meal = {
            'meal_type': meal_type,
            'ingredients': ingredients,
            'total_kcal': kcal,
            'total_protein': protein,
            'total_carbs': carbs,
            'total_fat': fat,
            'instructions': None
        }

        meals.append(meal)

    return meals


def parse_meal_macros(section_content: str) -> tuple:
    """Extract macros from a meal section."""

    # Find the kcal value first (most reliable marker)
    kcal_match = re.search(r'(\d+)\s*kcal', section_content)
    kcal = int(kcal_match.group(1)) if kcal_match else 0

    # Find protein (XXg P or XX g P)
    protein_match = re.search(r'(\d+)g?\s*P(?:\s|$|[^a-zA-Z])', section_content)
    protein = int(protein_match.group(1)) if protein_match else 0

    # Find carbs (XXg KH)
    carbs_match = re.search(r'(\d+)g?\s*KH', section_content)
    carbs = int(carbs_match.group(1)) if carbs_match else 0

    # Find fat (XXg F)
    fat_match = re.search(r'(\d+)g?\s*F(?:\s|$|[^a-zA-Z])', section_content)
    fat = int(fat_match.group(1)) if fat_match else 0

    return protein, carbs, fat, kcal


def parse_ingredients_from_section(lines: list[str]) -> list[dict]:
    """Parse ingredients from a list of lines."""

    ingredients = []
    order_index = 0

    for line in lines:
        # Clean the line - remove trailing macros
        clean_line = line.strip()
        if not clean_line:
            continue

        # Skip lines that are just macros
        if re.match(r'^[\d\s]+g?\s*(P|KH|F|kcal)?\s*$', clean_line):
            continue

        # Remove trailing macro values (they appear at the end of lines)
        # Pattern: number followed by g/P/KH/F/kcal at end of line
        clean_line = re.sub(r'\s+\d+g?\s*(P|KH|F)?\s*$', '', clean_line)
        clean_line = re.sub(r'\s+\d+\s*kcal\s*$', '', clean_line)
        clean_line = clean_line.strip()

        if not clean_line:
            continue

        # Try to parse as ingredient
        ingredient = parse_ingredient_line_v2(clean_line)
        if ingredient:
            ingredient['order_index'] = order_index
            ingredients.append(ingredient)
            order_index += 1

    return ingredients


def parse_ingredient_line_v2(line: str) -> dict | None:
    """Parse a single ingredient line."""

    # Skip very short lines
    if len(line) < 3:
        return None

    # Skip lines that look like just continuation text
    if line.startswith('(') and not re.search(r'^\(\d+', line):
        return None

    # Common patterns - order matters (most specific first)
    patterns = [
        # 2x200g Product
        (r'^(\d+)x(\d+)(g|ml)\s+(.+)$', lambda m: {
            'quantity': float(m.group(1)) * float(m.group(2)),
            'unit': m.group(3),
            'product_name': m.group(4).strip()
        }),
        # 6x60g Product
        (r'^(\d+)x(\d+)(g|ml)\s+(.+)$', lambda m: {
            'quantity': float(m.group(1)) * float(m.group(2)),
            'unit': m.group(3),
            'product_name': m.group(4).strip()
        }),
        # 125g (1 Beutel) Product - quantity with parenthetical note
        (r'^(\d+)(g|ml)\s*\([^)]+\)\s+(.+)$', lambda m: {
            'quantity': float(m.group(1)),
            'unit': m.group(2),
            'product_name': m.group(3).strip()
        }),
        # 300g Product
        (r'^(\d+)(g|ml)\s+(.+)$', lambda m: {
            'quantity': float(m.group(1)),
            'unit': m.group(2),
            'product_name': m.group(3).strip()
        }),
        # 1 EL/TL Product
        (r'^(\d+)\s*(EL|TL)\s+(.+)$', lambda m: {
            'quantity': float(m.group(1)),
            'unit': m.group(2),
            'product_name': m.group(3).strip()
        }),
        # 5 Eier (number + word starting with capital)
        (r'^(\d+)\s+([A-ZÄÖÜ][a-zA-ZäöüÄÖÜß\s]+.*)$', lambda m: {
            'quantity': float(m.group(1)),
            'unit': 'Stück',
            'product_name': m.group(2).strip()
        }),
        # 30 REWE Bio... (number + brand)
        (r'^(\d+)\s+(REWE|ja!|[A-Z]{2,}.+)$', lambda m: {
            'quantity': float(m.group(1)),
            'unit': 'Stück',
            'product_name': m.group(2).strip()
        }),
    ]

    for pattern, extractor in patterns:
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            try:
                result = extractor(match)
                # Clean up product name
                result['product_name'] = result['product_name'].strip()
                # Remove any remaining macro values from product name
                result['product_name'] = re.sub(r'\s+\d+g?\s*(P|KH|F)?$', '', result['product_name'])
                result['product_name'] = re.sub(r'\s+\d+\s*kcal$', '', result['product_name'])
                result['product_name'] = result['product_name'].strip()

                # Skip if product name is too short or looks like a measurement
                if len(result['product_name']) < 2:
                    continue
                if result['product_name'] in ['g', 'ml', 'EL', 'TL', 'P', 'KH', 'F', 'kcal']:
                    continue

                # Add default macro values
                result['kcal'] = 0
                result['protein'] = 0
                result['carbs'] = 0
                result['fat'] = 0
                return result
            except:
                continue

    return None


def clear_existing_meal_plans(db: Session):
    """Clear all existing meal plans before re-import."""
    count = db.query(MealPlan).count()
    if count > 0:
        print(f"Clearing {count} existing meal plans...")
        db.query(Ingredient).delete()
        db.query(Meal).delete()
        db.query(MealPlan).delete()
        db.commit()
        print("Cleared.")


def import_to_database(meal_plans: list[dict], db: Session):
    """Import parsed meal plans to database."""

    for plan_data in meal_plans:
        # Create meal plan
        meal_plan = MealPlan(
            level=plan_data['level'],
            day_number=plan_data['day_number'],
            gender=plan_data['gender'],
            total_kcal=plan_data['total_kcal'],
            total_protein=plan_data['total_protein'],
            total_carbs=plan_data['total_carbs'],
            total_fat=plan_data['total_fat'],
            name=plan_data['name'],
            description=plan_data['description'],
        )

        # Create meals
        for i, meal_data in enumerate(plan_data['meals']):
            meal = Meal(
                meal_type=meal_data['meal_type'],
                order_index=i,
                instructions=meal_data.get('instructions'),
                total_kcal=meal_data['total_kcal'],
                total_protein=meal_data['total_protein'],
                total_carbs=meal_data['total_carbs'],
                total_fat=meal_data['total_fat'],
            )

            # Create ingredients
            for ing_data in meal_data['ingredients']:
                ingredient = Ingredient(
                    product_name=ing_data['product_name'],
                    quantity=ing_data['quantity'],
                    unit=ing_data['unit'],
                    kcal=ing_data.get('kcal', 0),
                    protein=ing_data.get('protein', 0),
                    carbs=ing_data.get('carbs', 0),
                    fat=ing_data.get('fat', 0),
                    order_index=ing_data['order_index'],
                )
                meal.ingredients.append(ingredient)

            meal_plan.meals.append(meal)

        db.add(meal_plan)
        print(f"  Added: Level {plan_data['level']} Tag {plan_data['day_number']} ({plan_data['gender']})")

    db.commit()
    print(f"\nCommitted {len(meal_plans)} meal plans to database")


def main():
    """Main import function."""

    print("=" * 60)
    print("SLOTH Meal Plan Import v2")
    print("=" * 60)

    # File paths (relative to project root)
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    maenner_file = os.path.join(base_path, 'maenner_layout.txt')
    frauen_file = os.path.join(base_path, 'frauen_layout.txt')

    # Check files exist
    if not os.path.exists(maenner_file):
        print(f"Error: Male plans file not found: {maenner_file}")
        return
    if not os.path.exists(frauen_file):
        print(f"Error: Female plans file not found: {frauen_file}")
        return

    print(f"\nParsing male plans from: {maenner_file}")
    male_plans = parse_meal_plan_file(maenner_file, 'male')
    print(f"Parsed {len(male_plans)} male meal plans\n")

    print(f"Parsing female plans from: {frauen_file}")
    female_plans = parse_meal_plan_file(frauen_file, 'female')
    print(f"Parsed {len(female_plans)} female meal plans\n")

    all_plans = male_plans + female_plans
    print(f"Total plans to import: {len(all_plans)}")

    # Import to database
    print("\n" + "=" * 60)
    print("Importing to database...")
    print("=" * 60)

    db = SessionLocal()
    try:
        # Clear existing data first
        clear_existing_meal_plans(db)

        import_to_database(all_plans, db)
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("Import complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
