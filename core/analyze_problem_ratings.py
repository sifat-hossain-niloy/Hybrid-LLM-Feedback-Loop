"""
Analyze the rating distribution of problems in the problems folder
"""
import os
import json
from collections import Counter, defaultdict


def analyze_problem_ratings(problems_dir="problems"):
    """Analyze and display rating distribution of problems"""
    
    print("📊 ANALYZING PROBLEM RATINGS")
    print("=" * 70)
    
    if not os.path.exists(problems_dir):
        print(f"❌ Directory '{problems_dir}' not found")
        return
    
    # Collect all ratings
    ratings = []
    problems_by_rating = defaultdict(list)
    no_rating = []
    
    # Read all problem files
    problem_files = [f for f in os.listdir(problems_dir) if f.endswith('.json')]
    
    print(f"\n📁 Found {len(problem_files)} problem files\n")
    
    for filename in problem_files:
        filepath = os.path.join(problems_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                problem_data = json.load(f)
                
                rating = problem_data.get('rating', 'Not found')
                problem_id = filename.replace('.json', '')
                
                if rating == 'Not found' or not rating:
                    no_rating.append(problem_id)
                else:
                    # Convert to int if it's a string number
                    try:
                        rating_int = int(rating)
                        ratings.append(rating_int)
                        problems_by_rating[rating_int].append(problem_id)
                    except (ValueError, TypeError):
                        no_rating.append(problem_id)
        
        except Exception as e:
            print(f"⚠️  Error reading {filename}: {e}")
    
    # Statistics
    total_problems = len(problem_files)
    problems_with_rating = len(ratings)
    problems_without_rating = len(no_rating)
    
    print("=" * 70)
    print("📈 SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Total Problems:             {total_problems}")
    print(f"Problems with Rating:       {problems_with_rating} ({problems_with_rating/total_problems*100:.1f}%)")
    print(f"Problems without Rating:    {problems_without_rating} ({problems_without_rating/total_problems*100:.1f}%)")
    
    if ratings:
        print(f"\nRating Range:               {min(ratings)} - {max(ratings)}")
        print(f"Average Rating:             {sum(ratings)/len(ratings):.0f}")
        print(f"Median Rating:              {sorted(ratings)[len(ratings)//2]}")
    
    # Rating distribution
    print("\n" + "=" * 70)
    print("📊 RATING DISTRIBUTION")
    print("=" * 70)
    
    rating_counts = Counter(ratings)
    
    # Sort by rating
    for rating in sorted(rating_counts.keys()):
        count = rating_counts[rating]
        percentage = (count / problems_with_rating) * 100
        bar = "█" * int(percentage / 2)  # Scale bar to fit console
        
        print(f"{rating:>6} | {count:>3} problems ({percentage:>5.1f}%) {bar}")
    
    # Grouped by 100s
    print("\n" + "=" * 70)
    print("📊 GROUPED BY 100s")
    print("=" * 70)
    
    grouped = defaultdict(int)
    for rating in ratings:
        group = (rating // 100) * 100
        grouped[group] += 1
    
    for group in sorted(grouped.keys()):
        count = grouped[group]
        percentage = (count / problems_with_rating) * 100
        bar = "█" * int(percentage / 2)
        
        print(f"{group:>4}-{group+99:<4} | {count:>3} problems ({percentage:>5.1f}%) {bar}")
    
    # Target range (1200-1800)
    print("\n" + "=" * 70)
    print("🎯 TARGET RANGE (1200-1800)")
    print("=" * 70)
    
    in_range = [r for r in ratings if 1200 <= r <= 1800]
    out_of_range = [r for r in ratings if r < 1200 or r > 1800]
    
    print(f"In Range (1200-1800):       {len(in_range)} problems ({len(in_range)/problems_with_rating*100:.1f}%)")
    print(f"Below 1200:                 {len([r for r in ratings if r < 1200])} problems")
    print(f"Above 1800:                 {len([r for r in ratings if r > 1800])} problems")
    
    # Problems without rating
    if no_rating:
        print("\n" + "=" * 70)
        print(f"⚠️  PROBLEMS WITHOUT RATING ({len(no_rating)})")
        print("=" * 70)
        for i, prob_id in enumerate(sorted(no_rating)[:20], 1):
            print(f"  {i:>2}. {prob_id}")
        if len(no_rating) > 20:
            print(f"  ... and {len(no_rating) - 20} more")
    
    # Detailed breakdown for target range
    print("\n" + "=" * 70)
    print("📋 DETAILED BREAKDOWN (1200-1800)")
    print("=" * 70)
    
    for rating in range(1200, 1900, 100):
        range_start = rating
        range_end = rating + 99
        in_subrange = [r for r in ratings if range_start <= r <= range_end]
        
        if in_subrange:
            print(f"\n{range_start}-{range_end}: {len(in_subrange)} problems")
            
            # Show distribution within this range
            subrange_counts = Counter(in_subrange)
            for r in sorted(subrange_counts.keys()):
                count = subrange_counts[r]
                print(f"  {r}: {count} problem{'s' if count > 1 else ''}")
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    
    return {
        'total': total_problems,
        'with_rating': problems_with_rating,
        'without_rating': problems_without_rating,
        'in_target_range': len(in_range),
        'ratings': ratings,
        'problems_by_rating': dict(problems_by_rating)
    }


if __name__ == "__main__":
    results = analyze_problem_ratings()

