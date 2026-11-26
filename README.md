# The World Today — Thursday 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/DavidQlla06/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/DavidQlla06/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

Entry for the [make.fun news-image-20261126](https://make.fun/bounty/news-image-20261126)
competition: one image summing up the world's news of Thursday 26 November 2026.

## The image

A newspaper front page — **THE WORLD TODAY** — drawn by `generate.py`
from the day's stories in `stories.json`:

- **Lead:** Houthis strike Saudi Arabia's biggest refinery, Ras Tanura
  (550,000 barrels a day), a second night of attacks after the Riyadh
  tower strike wounded 11.
- **Map:** 12 flash points, from Ras Tanura and Gaza to Moscow, Jiuquan
  and Dhaka.
- **Markets:** Nasdaq −3.1%, S&P 500 −2.2%, Dow −728 pts, Nvidia −6%,
  Brent $92, gold $3,485.
- **The day's news:** 12 stories — US tariffs on 14 economies, the
  leaked 490,000 Russian war dead, Kyiv's refinery strikes, Huawei's
  guilty verdict, Pakistan's first astronaut, and more — plus a wire
  ticker with six briefs.

## How it runs

`main.py` copies the finished `entry.png` (1024×1024, under 1 MiB) to
`/output/entry.png`. The image is built offline, so both grading runs
write the same bytes. Regenerate it locally with:

```sh
python3 generate.py
```

## License

MIT — see [LICENSE](LICENSE).
