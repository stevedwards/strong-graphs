import tqdm


n = 10000000
with tqdm.tqdm(total=n) as bar:
    for _ in range(n):
        bar.update()