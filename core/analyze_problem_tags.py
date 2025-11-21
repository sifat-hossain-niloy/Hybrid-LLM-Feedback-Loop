import os
import json
from collections import defaultdict

def analyze_problem_tags(problems_dir="problems"):
    """
    Analyzes the tag distribution of problems in the specified directory.
    """
    print("🏷️  ANALYZING PROBLEM TAGS")
    print("=" * 60)

    tag_counts = defaultdict(int)
    tag_to_problems = defaultdict(list)  # Store which problems have each tag
    total_problems = 0
    problems_with_tags = 0
    problems_without_tags = 0

    if not os.path.exists(problems_dir):
        print(f"Error: Directory '{problems_dir}' not found.")
        return

    problem_files = [f for f in os.listdir(problems_dir) if f.endswith(".json")]
    total_problems = len(problem_files)
    print(f"\n📁 Found {total_problems} problem files")
    print("=" * 60)

    for filename in problem_files:
        filepath = os.path.join(problems_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                problem_data = json.load(f)
                tags = problem_data.get("tags", [])
                
                if tags and isinstance(tags, list) and len(tags) > 0:
                    problems_with_tags += 1
                    for tag in tags:
                        tag_counts[tag] += 1
                        tag_to_problems[tag].append(filename.replace('.json', ''))
                else:
                    problems_without_tags += 1
                    
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON from {filename}: {e}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

    print("\n📈 SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Problems:             {total_problems}")
    print(f"Problems with Tags:         {problems_with_tags} ({problems_with_tags/total_problems:.1%})" if total_problems > 0 else "0")
    print(f"Problems without Tags:      {problems_without_tags} ({problems_without_tags/total_problems:.1%})" if total_problems > 0 else "0")
    print(f"Unique Tags Found:          {len(tag_counts)}")

    print("\n🏷️  TAG DISTRIBUTION (Sorted by Frequency)")
    print("=" * 60)
    
    if tag_counts:
        # Sort tags by count (descending)
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        max_count = max(tag_counts.values())
        
        print(f"{'Tag':<35} | {'Count':>5} | {'% of Total':>10} | {'Visualization'}")
        print("-" * 60)
        
        for tag, count in sorted_tags:
            percentage = (count / total_problems) * 100
            # Simple bar chart visualization (scale to fit)
            bar_length = int((count / max_count) * 30)
            bar = '█' * bar_length
            print(f"{tag:<35} | {count:>5} | {percentage:>9.1f}% | {bar}")
    else:
        print("No tag data available.")
    
    # Top 10 most common tags with examples
    print("\n📊 TOP 10 MOST COMMON TAGS (with examples)")
    print("=" * 60)
    
    if sorted_tags:
        for i, (tag, count) in enumerate(sorted_tags[:10], 1):
            example_problems = tag_to_problems[tag][:3]  # Show first 3 examples
            examples_str = ", ".join(example_problems)
            print(f"{i:2d}. {tag:<30} ({count:3d} problems)")
            print(f"    Examples: {examples_str}")
            print()
    
    # Tag co-occurrence analysis
    print("\n🔗 TAG STATISTICS")
    print("=" * 60)
    
    tags_per_problem = []
    for filename in problem_files:
        filepath = os.path.join(problems_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                problem_data = json.load(f)
                tags = problem_data.get("tags", [])
                if tags and isinstance(tags, list):
                    tags_per_problem.append(len(tags))
        except:
            pass
    
    if tags_per_problem:
        avg_tags = sum(tags_per_problem) / len(tags_per_problem)
        min_tags = min(tags_per_problem)
        max_tags = max(tags_per_problem)
        
        print(f"Average tags per problem:   {avg_tags:.2f}")
        print(f"Min tags per problem:       {min_tags}")
        print(f"Max tags per problem:       {max_tags}")
        
        # Distribution of number of tags
        print("\n📊 DISTRIBUTION: Number of Tags per Problem")
        print("=" * 60)
        from collections import Counter
        tag_count_dist = Counter(tags_per_problem)
        for num_tags in sorted(tag_count_dist.keys()):
            count = tag_count_dist[num_tags]
            percentage = (count / len(tags_per_problem)) * 100
            bar = '█' * int(percentage / 2)
            print(f"{num_tags:2d} tags: {count:3d} problems ({percentage:5.1f}%) {bar}")

    print("\n" + "=" * 60)
    print("✅ TAG ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    analyze_problem_tags()

