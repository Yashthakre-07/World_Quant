def test_splitting(n_total, group_name):
    print(f"--- Testing {group_name} with {n_total} alphas ---")
    regular_tasks = [f"alpha_{i}" for i in range(n_total)]
    
    batches = []
    # Splitting math
    if regular_tasks:
        if n_total <= 40:
            q = n_total // 4
            r = n_total % 4
            size1 = q + (1 if r >= 1 else 0)
            size2 = q + (1 if r >= 2 else 0)
            size3 = q + (1 if r >= 3 else 0)
            size4 = q
            
            idx = 0
            for size in [size1, size2, size3, size4]:
                if size > 0:
                    batches.append(regular_tasks[idx:idx + size])
                    idx += size
        else:
            active_regular = regular_tasks[:40]
            for i in range(0, 40, 10):
                batches.append(active_regular[i:i + 10])
                
    # Slot assignment
    for slot_offset, batch in enumerate(batches, 1):
        if group_name == "Group A":
            slot_idx = slot_offset
        else:
            slot_idx = slot_offset + 4
        print(f"  Slot {slot_idx}: {len(batch)} alphas -> {batch}")
    print()

if __name__ == "__main__":
    test_splitting(40, "Group A")
    test_splitting(40, "Group B")
    test_splitting(38, "Group A")
    test_splitting(3, "Group B")
    test_splitting(45, "Group A")
