# repo-tn

Official extension repository for `TetoNova`.

This repository is intended to host:

- the public `index.json` consumed by TetoNova
- official extension bundle manifests
- compat-import metadata and seed catalogs where needed

## Raw Index URL

```text
https://raw.githubusercontent.com/dilescendol/repo-tn/main/index.json
```

## Current Structure

```text
index.json
bundles/
compat/
```

## Current Official Wave

<!-- official-wave:start -->
_Auto-generated on 20 Apr 2026 10:46 UTC_

| Active | Guarded | Thin | Dead/Error |
| --- | --- | --- | --- |
| **2** | **8** | **0** | **0** |

| Source | Web status | HTTP | Probe |
| --- | --- | --- | --- |
| Oploverz | 🟢 Active | 200 | [Open](https://anime.oploverz.ac/) |
| Oppadrama | 🟢 Active | 200 | [Open](http://45.11.57.129/series/?status=&type=&order=update) |
| AnimeSail | 🟡 Guarded | 200 | [Open](https://154.26.137.28/rilisan-anime-terbaru/page/) |
| AnimeXin | 🟡 Guarded | 200 | [Open](https://animexin.dev/anime/?order=update&status=&type=) |
| Anixverse | 🟡 Guarded | 200 | [Open](https://anixverseone.com/anime/?order=update) |
| Anoboy | 🟡 Guarded | 200 | [Open](https://ww1.anoboy.boo/) |
| Donghub | 🟡 Guarded | 200 | [Open](https://donghub.vip/anime/?order=update) |
| Hidoristream | 🟡 Guarded | 200 | [Open](https://v2.hidoristream.online/) |
| PencuriMovie | 🟡 Guarded | 200 | [Open](https://ww99.pencurimovie.bond/movies) |
| Winbu | 🟡 Guarded | 200 | [Open](https://winbu.net/film/) |
| Anichin | 🟠 Blocked | 403 | [Open](https://anichin.moe/anime/?order=update) |
| Animasu | 🟠 Blocked | 403 | [Open](https://v1.animasu.app/anime-sedang-tayang-terbaru/) |
| Kuramanime | 🟠 Blocked | 403 | [Open](https://v17.kuramanime.ink/) |
| NontonAnimeID | 🟠 Blocked | 403 | [Open](https://s11.nontonanimeid.boats/) |
| Otakudesu | 🟠 Blocked | 403 | [Open](https://otakudesu.blog/ongoing-anime/page/1/) |
| Samehadaku | 🟠 Blocked | 403 | [Open](https://v2.samehadaku.how/) |

Detail report: [`docs/SOURCE_STATUS.md`](docs/SOURCE_STATUS.md)
<!-- official-wave:end -->

## Notes

- `index.json` is the primary entrypoint for app-side repo refresh.
- Bundle manifests should stay lightweight and app-compatible.
- Compat seed catalogs can live alongside bundles for migration pilots such as `Anichin`.
