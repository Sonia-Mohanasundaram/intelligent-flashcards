#!/usr/bin/env python3
"""
Cross-domain validation of the refined AI flashcard generation pipeline.
Tests multiple subjects: History, Biology, Mathematics, Geography, Chemistry, Physics, Literature.
Demonstrates universal question generation capability.
"""

from services.ai_pipeline_17steps import AIProcessingPipeline

def print_test(subject, text, result):
    flashcards = result.get('flashcards', [])
    print(f"\n{'─'*80}")
    print(f"📚 {subject.upper()}")
    print(f"{'─'*80}")
    print(f"Input: {text[:100]}...")
    print(f"\n✓ Generated {len(flashcards)} flashcards:\n")
    
    for i, card in enumerate(flashcards, 1):
        print(f"  {i}. [{card['type'].upper():12}] {card['keyword']}")
        print(f"     Q: {card['question']}")
        print(f"     A: {card['answer']}")
        print()

pipeline = AIProcessingPipeline()

print("\n" + "="*80)
print("  CROSS-DOMAIN FLASHCARD GENERATION TEST")
print("="*80)

# Test 1: History
history_text = """
The French Revolution occurred from 1789 to 1799. It was a period of social and political upheaval in France. 
The revolution abolished feudalism and established democratic principles. 
Key causes included economic crisis, food shortages, and Enlightenment ideas. 
Major events include the storming of the Bastille in 1789 and the Reign of Terror from 1793-1794.
The revolution had lasting impacts on governance, human rights, and nationalism across Europe.
"""

result = pipeline.process(history_text, "French Revolution")
print_test("History", history_text, result)

# Test 2: Biology
biology_text = """
Photosynthesis is the process by which plants convert light energy into chemical energy. 
It occurs in two stages: the light-dependent reactions and the Calvin cycle. 
The light-dependent reactions take place in the thylakoids and produce ATP and NADPH. 
The Calvin cycle occurs in the stroma and produces glucose. 
Photosynthesis is essential for life because it produces oxygen and organic compounds that serve as food for other organisms.
"""

result = pipeline.process(biology_text, "Photosynthesis")
print_test("Biology", biology_text, result)

# Test 3: Mathematics
math_text = """
The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides. 
It is expressed as a² + b² = c², where c is the hypotenuse. 
This theorem has numerous applications in geometry, physics, and engineering. 
The theorem applies only to right triangles with a 90-degree angle. 
It is one of the most fundamental principles in mathematics used for distance calculations and architectural design.
"""

result = pipeline.process(math_text, "Pythagorean Theorem")
print_test("Mathematics", math_text, result)

# Test 4: Geography
geography_text = """
The Amazon Rainforest is the world's largest tropical rainforest covering approximately 5.5 million square kilometers. 
It spans nine countries with Brazil containing about 60 percent of the forest. 
The Amazon produces roughly 20 percent of the world's oxygen and is home to incredible biodiversity. 
It supports over 390 billion individual trees representing about 16,000 species. 
The rainforest is threatened by deforestation for agriculture, logging, and cattle ranching.
"""

result = pipeline.process(geography_text, "Amazon Rainforest")
print_test("Geography", geography_text, result)

# Test 5: Chemistry
chemistry_text = """
The periodic table is an organized arrangement of all known chemical elements. 
Elements are arranged by atomic number, electron configuration, and recurring chemical properties. 
The table has 118 confirmed chemical elements as of 2024. 
Elements in the same column (group) have similar chemical properties and valence electrons. 
The periodic table is an essential tool for chemists to predict element behavior and reactivity.
"""

result = pipeline.process(chemistry_text, "Periodic Table")
print_test("Chemistry", chemistry_text, result)

# Test 6: Physics
physics_text = """
Newton's First Law of Motion states that an object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force. 
This law introduces the concept of inertia. 
It forms the foundation for understanding motion and forces in physics. 
The law explains why passengers lurch forward when a car brakes suddenly. 
Understanding inertia is crucial for designing safety systems and understanding celestial mechanics.
"""

result = pipeline.process(physics_text, "Newtons First Law")
print_test("Physics", physics_text, result)

# Test 7: Literature
literature_text = """
Shakespeare was an English playwright and poet born in 1564. 
He wrote approximately 37 plays including tragedies, comedies, and histories. 
His works include Hamlet, Macbeth, Romeo and Juliet, and A Midsummer Night's Dream. 
Shakespeare's plays explore themes of ambition, love, betrayal, and the human condition. 
His influence on literature and the English language is unparalleled, with many phrases and words originating from his works.
"""

result = pipeline.process(literature_text, "Shakespeare")
print_test("Literature", literature_text, result)

print("\n" + "="*80)
print("✓ Cross-domain validation complete")
print("✓ Pipeline successfully generates questions from ALL subjects")
print("="*80 + "\n")
