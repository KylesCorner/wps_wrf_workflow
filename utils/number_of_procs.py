import math

def choose_wrf_ranks(e_we, e_sn, total_ranks):
    # Find factors of total_ranks
    factors = []
    for i in range(1, int(math.sqrt(total_ranks)) + 1):
        if total_ranks % i == 0:
            factors.append((i, total_ranks // i))
            factors.append((total_ranks // i, i))

    # Filter factors that divide the domain
    valid_pairs = [(nx, ny) for nx, ny in factors if e_we % nx == 0 and e_sn % ny == 0]

    # Pick the pair with nx >= ny and largest nx (more square-ish)
    if not valid_pairs:
        raise ValueError("No valid rank decomposition found")
    
    nx, ny = max(valid_pairs, key=lambda x: (x[0], x[1]))
    return nx, ny

e_we, e_sn = 400, 400
total_ranks = 128
nx, ny = choose_wrf_ranks(e_we, e_sn, total_ranks)
print(f"nproc_x = {nx}, nproc_y = {ny}")

